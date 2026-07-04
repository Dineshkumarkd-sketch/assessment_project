import React, { useState } from 'react';
import axios from 'axios';

const ProductForm = ({ product, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: product?.name || '',
    description: product?.description || '',
    price: product?.price || '',
    category: product?.category || ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!formData.name || !formData.price) {
      setError('Name and price are required');
      return;
    }

    if (isNaN(formData.price) || Number(formData.price) <= 0) {
      setError('Price must be a valid positive number');
      return;
    }
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const config = { headers: { Authorization: `Bearer ${token}` } };
      
      if (product) {
        // Update existing
        await axios.put(`http://localhost:5000/api/products/${product._id}`, formData, config);
      } else {
        // Create new
        await axios.post('http://localhost:5000/api/products', formData, config);
      }
      onSave(); // Trigger refresh in parent
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <p className="error-text" style={{ marginBottom: '1rem' }}>{error}</p>}
      
      <div className="form-group">
        <label>Product Name *</label>
        <input
          type="text"
          name="name"
          className="form-control"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label>Price ($) *</label>
        <input
          type="number"
          name="price"
          step="0.01"
          min="0.01"
          className="form-control"
          value={formData.price}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label>Category</label>
        <input
          type="text"
          name="category"
          className="form-control"
          value={formData.category}
          onChange={handleChange}
        />
      </div>
      
      <div className="form-group">
        <label>Description</label>
        <textarea
          name="description"
          className="form-control"
          value={formData.description}
          onChange={handleChange}
          rows="3"
        />
      </div>
      
      <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
        <button type="button" className="btn" style={{ backgroundColor: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-main)' }} onClick={onCancel} disabled={loading}>
          Cancel
        </button>
        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Saving...' : 'Save Product'}
        </button>
      </div>
    </form>
  );
};

export default ProductForm;
