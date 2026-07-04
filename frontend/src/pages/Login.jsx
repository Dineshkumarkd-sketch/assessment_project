import React, { useState, useEffect } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import axios from "axios";

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState(
    location.state?.message || ""
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (successMsg) {
      const timer = setTimeout(() => setSuccessMsg(""), 4000);
      return () => clearTimeout(timer);
    }
  }, [successMsg]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    console.log("========== LOGIN START ==========");
    console.log("FORM DATA:", formData);

    setError("");
    setSuccessMsg("");

    if (!formData.email || !formData.password) {
      setError("Please fill in all fields");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(
        "https://assessment-project-wpc9.onrender.com/api/auth/login",
        {
          email: formData.email,
          password: formData.password,
        }
      );

      console.log("API RESPONSE:", response.data);

      const token = response.data.token;
      const user = response.data.user;

      if (!token) {
        setError("Token not received");
        return;
      }

      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));

      console.log("TOKEN SAVED:", localStorage.getItem("token"));
      console.log("USER SAVED:", localStorage.getItem("user"));

      navigate("/dashboard");
    } catch (err) {
      console.log("LOGIN ERROR:", err);

      if (err.response) {
        console.log("STATUS:", err.response.status);
        console.log("DATA:", err.response.data);

        setError(err.response.data.message || "Login failed");
      } else {
        setError("Cannot connect to server");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Welcome Back</h2>

        {successMsg && <p className="success-text">{successMsg}</p>}

        {error && (
          <p
            className="error-text"
            style={{ textAlign: "center", marginBottom: "1rem" }}
          >
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              name="email"
              className="form-control"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              className="form-control"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <button className="btn" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>

        <p
          style={{
            textAlign: "center",
            marginTop: "1.5rem",
            color: "var(--text-muted)",
          }}
        >
          Don't have an account?{" "}
          <Link to="/register" style={{ color: "var(--primary)" }}>
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;