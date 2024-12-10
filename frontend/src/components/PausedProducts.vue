<template>
    <div>
      <h1>Productos Pausados Sin Stock</h1>
      <button @click="fetchPausedProducts">Consultar Productos</button>
      <div v-if="products.length > 0" class="cards-container">
        <div class="card" v-for="product in products" :key="product.id">
          <img :src="product.thumbnail" alt="Imagen del producto" />
          <h3>{{ product.title }}</h3>
          <p><strong>Precio:</strong> ${{ product.price }}</p>
          <p><strong>Categoría:</strong> {{ product.category_id }}</p>
          <p><strong>Estado:</strong> {{ product.status }}</p>
        </div>
      </div>
      <div v-else-if="loading">
        <p>Cargando productos...</p>
      </div>
      <div v-else>
        <p>No hay productos pausados sin stock para mostrar.</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        products: [], // Lista de productos pausados sin stock
        loading: false, // Indicador de carga
      };
    },
    methods: {
      async fetchPausedProducts() {
        try {
          this.loading = true;
          this.products = [];
          const token = prompt("Introduce tu Access Token:");
          const response = await fetch(`http://127.0.0.1:5000/paused-products?token=${token}`);
          if (!response.ok) {
            throw new Error(`Error: ${response.status} - ${response.statusText}`);
          }
          const data = await response.json();
          this.products = data.results;
        } catch (error) {
          console.error("Error al consultar productos pausados:", error);
        } finally {
          this.loading = false;
        }
      },
    },
  };
  </script>
  
  <style scoped>
  h1 {
    text-align: center;
    color: #4CAF50;
  }
  button {
    display: block;
    margin: 20px auto;
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    border-radius: 5px;
    font-size: 16px;
  }
  button:hover {
    background-color: #45a049;
  }
  .cards-container {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: center;
  }
  .card {
    border: 1px solid #ddd;
    border-radius: 5px;
    width: 300px;
    padding: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
  }
  .card img {
    max-width: 100%;
    height: auto;
    border-radius: 5px;
  }
  .card h3 {
    margin: 10px 0;
  }
  .card p {
    margin: 5px 0;
  }
  </style>
  