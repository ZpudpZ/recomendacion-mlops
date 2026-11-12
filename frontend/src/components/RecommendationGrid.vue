<!-- Ubicación: frontend/src/components/RecommendationGrid.vue -->
<script setup>
import { ref, computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps({
  recommendations: {
    type: Array,
    default: () => []
  },
  isColdStart: {
    type: Boolean,
    default: false
  },
  queriedUser: {
    type: Number,
    default: 196
  },
  userInteractionsCount: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['fetch-recommendations'])

const userIdInput = ref(props.queriedUser)
const topNInput = ref(10)

const handleQuery = () => {
  emit('fetch-recommendations', {
    userId: userIdInput.value,
    topN: topNInput.value
  })
}

const chartData = computed(() => {
  const labels = props.recommendations.map((item) => `ID #${item.item_id}`)
  const scores = props.recommendations.map((item) => item.estimated_score)

  return {
    labels,
    datasets: [
      {
        label: 'Score Predicho SVD (Escala 1.0 - 5.0)',
        data: scores,
        backgroundColor: scores.map((_, idx) =>
          idx < 3 ? 'rgba(16, 185, 129, 0.8)' : 'rgba(37, 99, 235, 0.75)'
        ),
        borderColor: scores.map((_, idx) =>
          idx < 3 ? '#10b981' : '#2563eb'
        ),
        borderWidth: 1,
        borderRadius: 4
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#cbd5e1',
        font: { family: 'monospace', size: 11 }
      }
    },
    tooltip: {
      backgroundColor: '#0f172a',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      borderColor: '#334155',
      borderWidth: 1,
      callbacks: {
        afterLabel: (ctx) => {
          const item = props.recommendations[ctx.dataIndex]
          return item ? `${item.title} (${item.genre})` : ''
        }
      }
    }
  },
  scales: {
    x: {
      ticks: { color: '#94a3b8', font: { family: 'monospace', size: 11 } },
      grid: { color: 'rgba(51, 65, 85, 0.35)' }
    },
    y: {
      min: 1,
      max: 5,
      ticks: { color: '#94a3b8', stepSize: 0.5 },
      grid: { color: 'rgba(51, 65, 85, 0.35)' }
    }
  }
}
</script>

<template>
  <section class="panel">
    <div class="top-controls">
      <div class="header-info">
        <h2>MOTOR DE INFERENCIA TOP-N | USUARIO #{{ queriedUser }}</h2>
        <p class="sub-text">
          Interacciones históricas registradas: <strong>{{ userInteractionsCount }}</strong>
        </p>
      </div>

      <form @submit.prevent="handleQuery" class="query-form">
        <div class="input-inline">
          <label for="uid">ID Usuario</label>
          <input
            id="uid"
            type="number"
            v-model.number="userIdInput"
            min="1"
            required
          />
        </div>

        <div class="input-inline">
          <label for="topn">Top-N</label>
          <input
            id="topn"
            type="number"
            v-model.number="topNInput"
            min="3"
            max="30"
            required
          />
        </div>

        <button type="submit" class="btn-emerald" :disabled="loading">
          {{ loading ? 'PROCESANDO...' : 'CONSULTAR RECOMENDACIONES' }}
        </button>
      </form>
    </div>

    <div class="status-bar">
      <span :class="['badge', isColdStart ? 'badge-slate' : 'badge-emerald']">
        {{ isColdStart ? 'MODO COLD-START: POPULARIDAD GLOBAL' : 'MODO PERSONALIZADO: FACTORIZACIÓN MATRICIAL SVD' }}
      </span>
    </div>

    <div class="content-split">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>RANK</th>
              <th>ID</th>
              <th>TÍTULO Y CATEGORÍA</th>
              <th>NORMA ||q_i||</th>
              <th>CONFIANZA</th>
              <th>SCORE SVD</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in recommendations" :key="item.item_id">
              <td class="mono-muted">{{ index + 1 }}</td>
              <td class="mono-id">#{{ item.item_id }}</td>
              <td>
                <div class="title-text">{{ item.title }}</div>
                <div class="genre-text">{{ item.genre }}</div>
              </td>
              <td class="mono-muted">{{ item.latent_norm.toFixed(3) }}</td>
              <td>
                <div class="progress-track">
                  <div
                    class="progress-fill"
                    :style="{ width: item.confidence_pct + '%' }"
                  ></div>
                </div>
                <span class="mono-small">{{ item.confidence_pct }}%</span>
              </td>
              <td class="score-highlight">{{ item.estimated_score.toFixed(4) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="chart-container">
        <div class="chart-header">DISTRIBUCIÓN DE SCORES PREDICHOS</div>
        <div class="chart-body">
          <Bar
            v-if="recommendations.length > 0"
            :data="chartData"
            :options="chartOptions"
          />
        </div>
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

.top-controls {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #334155;
}

.header-info h2 {
  margin: 0;
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  color: #f8fafc;
  font-weight: 700;
}

.sub-text {
  margin: 0.3rem 0 0;
  font-size: 0.78rem;
  color: #94a3b8;
}

.sub-text strong {
  color: #f8fafc;
}

.query-form {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.input-inline {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.input-inline label {
  font-size: 0.72rem;
  color: #94a3b8;
  text-transform: uppercase;
}

.input-inline input {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #f8fafc;
  padding: 0.5rem 0.65rem;
  border-radius: 0.375rem;
  font-family: monospace;
  font-size: 0.88rem;
  width: 110px;
}

.btn-emerald {
  padding: 0.55rem 1rem;
  background-color: #10b981;
  color: #0f172a;
  border: 1px solid #059669;
  border-radius: 0.375rem;
  font-weight: 700;
  font-size: 0.76rem;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: background-color 0.15s;
}

.btn-emerald:hover:not(:disabled) {
  background-color: #059669;
  color: #f8fafc;
}

.btn-emerald:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.status-bar {
  margin: 0.9rem 0;
  display: flex;
  justify-content: flex-end;
}

.badge {
  font-family: monospace;
  font-size: 0.72rem;
  padding: 0.25rem 0.65rem;
  border-radius: 0.25rem;
  font-weight: 600;
}

.badge-emerald {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.35);
}

.badge-slate {
  background-color: #0f172a;
  color: #94a3b8;
  border: 1px solid #334155;
}

.content-split {
  display: grid;
  grid-template-columns: 1.25fr 1fr;
  gap: 1.25rem;
  align-items: stretch;
}

.table-container {
  overflow-x: auto;
  max-height: 420px;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.82rem;
}

.data-table th {
  position: sticky;
  top: 0;
  background-color: #0f172a;
  color: #94a3b8;
  font-size: 0.7rem;
  padding: 0.7rem 0.75rem;
  border-bottom: 1px solid #334155;
  letter-spacing: 0.04em;
}

.data-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #1e293b;
}

.mono-muted {
  font-family: monospace;
  color: #64748b;
}

.mono-id {
  font-family: monospace;
  color: #cbd5e1;
}

.title-text {
  font-weight: 600;
  color: #f8fafc;
}

.genre-text {
  font-size: 0.7rem;
  color: #2563eb;
  font-weight: 600;
}

.progress-track {
  width: 65px;
  height: 5px;
  background-color: #1e293b;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 0.2rem;
}

.progress-fill {
  height: 100%;
  background-color: #10b981;
}

.mono-small {
  font-family: monospace;
  font-size: 0.7rem;
  color: #94a3b8;
}

.score-highlight {
  font-family: monospace;
  font-size: 0.92rem;
  font-weight: 700;
  color: #10b981;
}

.chart-container {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.chart-header {
  font-family: monospace;
  font-size: 0.74rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
  letter-spacing: 0.05em;
}

.chart-body {
  flex: 1;
  min-height: 340px;
  position: relative;
}

@media (max-width: 1150px) {
  .content-split {
    grid-template-columns: 1fr;
  }
}
</style>