<script setup>
defineProps({
  kpis: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <h2>MÉTRICAS DE VALIDACIÓN Y TELEMETRÍA</h2>
      <span class="meta-summary">
        USUARIOS ACTIVOS: {{ kpis.n_users }} | CATÁLOGO DE ÍTEMS: {{ kpis.n_items }}
      </span>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card border-cobalt">
        <span class="kpi-label">RMSE (Error Cuadrático Medio)</span>
        <strong class="kpi-value">{{ kpis.rmse.toFixed(4) }}</strong>
        <span class="kpi-sub">Muestras Test: {{ kpis.test_samples.toLocaleString() }}</span>
      </div>

      <div class="kpi-card border-emerald">
        <span class="kpi-label">MAE (Error Absoluto Medio)</span>
        <strong class="kpi-value">{{ kpis.mae.toFixed(4) }}</strong>
        <span class="kpi-sub">Muestras Train: {{ kpis.train_samples.toLocaleString() }}</span>
      </div>

      <div class="kpi-card border-slate">
        <span class="kpi-label">Dispersión de Matriz (Sparsity)</span>
        <strong class="kpi-value">{{ kpis.sparsity_pct.toFixed(2) }}%</strong>
        <span class="kpi-sub">Densidad de interacciones</span>
      </div>

      <div class="kpi-card border-emerald">
        <span class="kpi-label">Tiempo de Cómputo SVD</span>
        <strong class="kpi-value">{{ kpis.compute_time_ms.toFixed(1) }} ms</strong>
        <span class="kpi-sub">Latencia de ajuste y validación</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.panel {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1.25rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.panel-header h2 {
  margin: 0;
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  color: #f8fafc;
  font-weight: 700;
}

.meta-summary {
  font-family: monospace;
  font-size: 0.75rem;
  color: #94a3b8;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.kpi-card {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.border-cobalt {
  border-left: 3px solid #2563eb;
}

.border-emerald {
  border-left: 3px solid #10b981;
}

.border-slate {
  border-left: 3px solid #64748b;
}

.kpi-label {
  font-size: 0.73rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.kpi-value {
  font-family: monospace;
  font-size: 1.55rem;
  color: #f8fafc;
}

.kpi-sub {
  font-size: 0.72rem;
  color: #64748b;
}

@media (max-width: 1100px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>