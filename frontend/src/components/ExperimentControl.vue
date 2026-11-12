<script setup>
import { reactive } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['run-experiment'])

const form = reactive({
  n_factors: 100,
  n_epochs: 20,
  lr_all: 0.005,
  reg_all: 0.02,
  test_split: 0.2,
  sample_fraction: 0.6,
  update_active_model: true
})

const submitExperiment = () => {
  emit('run-experiment', { ...form })
}
</script>

<template>
  <aside class="panel">
    <div class="panel-header">
      <h2>CONFIGURACIÓN DEL MODELO SVD</h2>
      <span class="tag">HIPERPARÁMETROS</span>
    </div>

    <form @submit.prevent="submitExperiment" class="control-form">
      <div class="slider-group">
        <div class="slider-label">
          <label>Factores Latentes (n_factors)</label>
          <span class="mono-val">{{ form.n_factors }}</span>
        </div>
        <input
          type="range"
          v-model.number="form.n_factors"
          min="10"
          max="200"
          step="10"
        />
      </div>

      <div class="slider-group">
        <div class="slider-label">
          <label>Épocas SGD (n_epochs)</label>
          <span class="mono-val">{{ form.n_epochs }}</span>
        </div>
        <input
          type="range"
          v-model.number="form.n_epochs"
          min="5"
          max="60"
          step="5"
        />
      </div>

      <div class="slider-group">
        <div class="slider-label">
          <label>Tasa de Aprendizaje (lr_all)</label>
          <span class="mono-val">{{ form.lr_all.toFixed(4) }}</span>
        </div>
        <input
          type="range"
          v-model.number="form.lr_all"
          min="0.001"
          max="0.025"
          step="0.001"
        />
      </div>

      <div class="slider-group">
        <div class="slider-label">
          <label>Regularización L2 (reg_all)</label>
          <span class="mono-val">{{ form.reg_all.toFixed(3) }}</span>
        </div>
        <input
          type="range"
          v-model.number="form.reg_all"
          min="0.005"
          max="0.15"
          step="0.005"
        />
      </div>

      <div class="slider-group">
        <div class="slider-label">
          <label>Proporción de Validación (test_split)</label>
          <span class="mono-val">{{ (form.test_split * 100).toFixed(0) }}%</span>
        </div>
        <input
          type="range"
          v-model.number="form.test_split"
          min="0.1"
          max="0.4"
          step="0.05"
        />
      </div>

      <div class="slider-group">
        <div class="slider-label">
          <label>Muestreo del Dataset (sample_fraction)</label>
          <span class="mono-val">{{ (form.sample_fraction * 100).toFixed(0) }}%</span>
        </div>
        <input
          type="range"
          v-model.number="form.sample_fraction"
          min="0.2"
          max="1.0"
          step="0.1"
        />
      </div>

      <label class="checkbox-row">
        <input type="checkbox" v-model="form.update_active_model" />
        <span>Sincronizar modelo en producción tras evaluar</span>
      </label>

      <button type="submit" class="btn-primary" :disabled="props.loading">
        {{ props.loading ? 'EJECUTANDO ENTRENAMIENTO...' : 'EJECUTAR VALIDACIÓN EXPERIMENTAL' }}
      </button>
    </form>
  </aside>
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
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #334155;
}

.panel-header h2 {
  margin: 0;
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  color: #f8fafc;
  font-weight: 700;
}

.tag {
  font-family: monospace;
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  background-color: #0f172a;
  color: #94a3b8;
  border: 1px solid #334155;
  border-radius: 0.25rem;
}

.control-form {
  display: flex;
  flex-direction: column;
  gap: 1.05rem;
}

.slider-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.slider-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #cbd5e1;
}

.mono-val {
  font-family: monospace;
  color: #10b981;
  font-weight: 700;
}

input[type='range'] {
  width: 100%;
  accent-color: #2563eb;
  cursor: pointer;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #cbd5e1;
  cursor: pointer;
  margin-top: 0.25rem;
}

.btn-primary {
  margin-top: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #2563eb;
  color: #f8fafc;
  border: 1px solid #1d4ed8;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.78rem;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: background-color 0.15s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>