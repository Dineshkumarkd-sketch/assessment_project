import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProductForm from '../components/ProductForm';

const Dashboard = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  // ================= FETCH PRODUCTS =================
  const fetchProducts = async () => {
    setLoading(true);

    try {
      const token = localStorage.getItem('token');

      const response = await axios.get(
        'https://assessment-project-wpc9.onrender.com/api/products',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setProducts(response.data);
      setError('');
    } catch (err) {
      console.log(err.response?.data || err.message);

      setError('Failed to fetch products. Please try again.');

      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // ================= DELETE PRODUCT =================
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      const token = localStorage.getItem('token');

      await axios.delete(
        `https://assessment-project-wpc9.onrender.com/api/products/${id}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // FIXED STATE UPDATE
      setProducts((prev) => prev.filter((p) => p._id !== id));

    } catch (err) {
      alert('Failed to delete product');
    }
  };

  // ================= MODAL HANDLERS =================
  const openAddModal = () => {
    setEditingProduct(null);
    setIsModalOpen(true);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setIsModalOpen(true);
  };

  const handleProductSaved = () => {
    setIsModalOpen(false);
    fetchProducts(); // refresh list
  };

  // ================= LOADING =================
  if (loading) {
    return (
      <div className="dashboard">
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* HEADER */}
      <div className="dashboard-header">
        <h2>Your Products</h2>

        <button className="btn" style={{ width: 'auto' }} onClick={openAddModal}>
          + Add Product
        </button>
      </div>

      {/* ERROR */}
      {error && <p className="error-text">{error}</p>}

      {/* EMPTY STATE */}
      {!loading && products.length === 0 && !error && (
        <div
          style={{
            textAlign: 'center',
            padding: '3rem',
            backgroundColor: 'var(--bg-card)',
            borderRadius: '10px'
          }}
        >
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>
            You don't have any products yet.
          </p>

          <button className="btn" style={{ width: 'auto' }} onClick={openAddModal}>
            Create your first product
          </button>
        </div>
      )}

      {/* PRODUCT LIST */}
      <div className="product-grid">
        {products.map((product) => (
          <div key={product._id} className="product-card">
            <h3 className="product-title">{product.name}</h3>

            {product.category && (
              <span
                style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-muted)',
                  marginBottom: '0.5rem'
                }}
              >
                {product.category}
              </span>
            )}

            <p
              style={{
                color: 'var(--text-muted)',
                marginBottom: '1rem',
                flexGrow: 1
              }}
            >
              {product.description}
            </p>

            {/* FIXED PRICE */}
            <div className="product-price">
              ${Number(product.price || 0).toFixed(2)}
            </div>

            <div className="product-actions">
              <button
                className="btn"
                style={{ backgroundColor: '#3b82f6' }}
                onClick={() => openEditModal(product)}
              >
                Edit
              </button>

              <button
                className="btn btn-danger"
                onClick={() => handleDelete(product._id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* MODAL */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 style={{ marginBottom: '1.5rem' }}>
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h3>

            <ProductForm
              product={editingProduct}
              onSave={handleProductSaved}
              onCancel={() => setIsModalOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;