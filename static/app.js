// Mobile-friendly selection script
(() => {
  const selected = new Set();
  const cards = document.querySelectorAll('.card');
  const statsEl = document.getElementById('stats');

  function updateUI(){
    cards.forEach(btn => {
      const c = btn.dataset.card;
      if(selected.has(c)) btn.classList.add('selected'); else btn.classList.remove('selected');
    });
  }

  function showStats(obj){
    if(!obj.ok){
      statsEl.textContent = 'Error: ' + (obj.error||'Unknown');
      return;
    }
    const s = obj.stats;
    const pct = s.better_percent.toFixed(3);
    statsEl.textContent = `${s.category} — Rank ${s.rank} of ${s.total} (Top ${pct}% have better hands)`;
  }

  async function evaluateIfReady(){
    if(selected.size===3){
      statsEl.textContent = 'Evaluating...';
      const hand = Array.from(selected);
      try{
        const res = await fetch('/api/rank', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({hand})
        });
        const j = await res.json();
        showStats(j);
      }catch(err){
        statsEl.textContent = 'Network error';
      }
    }else{
      statsEl.textContent = `Select ${3 - selected.size} more card(s)`;
    }
  }

  // maintain insertion order for replacement behavior
  const order = [];
  cards.forEach(btn => {
    btn.addEventListener('click', e => {
      const c = btn.dataset.card;
      if(selected.has(c)){
        selected.delete(c);
        const idx = order.indexOf(c);
        if(idx>=0) order.splice(idx,1);
      }else{
        if(selected.size<3){
          selected.add(c);
          order.push(c);
        }else{
          // replace the oldest selected card with this one
          const oldest = order.shift();
          if(oldest){
            selected.delete(oldest);
          }
          selected.add(c);
          order.push(c);
        }
      }
      updateUI();
      evaluateIfReady();
    });
  });

  // initial message
  statsEl.textContent = 'Select 3 cards';
})();
