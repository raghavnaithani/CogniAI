document.addEventListener('DOMContentLoaded', () => {
  const textEl = document.getElementById('text');
  const routeBtn = document.getElementById('routeBtn');
  const clearBtn = document.getElementById('clearBtn');
  const resultEl = document.getElementById('result');

  async function routeText() {
    const text = textEl.value.trim();
    if (!text) {
      resultEl.innerText = 'Please enter text to route.';
      return;
    }
    resultEl.innerText = 'Routing...';
    try {
      const resp = await fetch(`/route?text=${encodeURIComponent(text)}`);
      const data = await resp.json();
      if (data.error) {
        resultEl.innerText = `Error: ${data.error}`;
      } else if (Array.isArray(data.bots) && data.bots.length > 0) {
        resultEl.innerHTML = `<strong>Matched bots:</strong> <code>${data.bots.join(', ')}</code>`;
      } else if (Array.isArray(data.ranked) && data.ranked.length > 0) {
        const items = data.ranked.map((item) => {
          const pct = Math.round(item.score * 100);
          return `<li><strong>${item.bot_id}</strong> <span class="score">${pct}%</span></li>`;
        }).join('');
        resultEl.innerHTML = `<strong>${data.message || 'Top matches:'}</strong><ul class="ranked">${items}</ul>`;
      } else if (data.error) {
        resultEl.innerText = `Error: ${data.error}`;
      } else {
        resultEl.innerText = JSON.stringify(data, null, 2);
      }
    } catch (err) {
      resultEl.innerText = `Request failed: ${err.message}`;
    }
  }

  routeBtn.addEventListener('click', routeText);
  clearBtn.addEventListener('click', () => {
    textEl.value = '';
    resultEl.innerText = '';
  });

  // quick demo text
  textEl.value = 'Bitcoin ETF approval drives institutional inflows and bullish sentiment.';
});
