import React from 'react';

const UserDetailsForm = ({ userDetails, setUserDetails, onSubmit }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-2xl font-semibold mb-4">Enter Your Details</h2>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Full Name"
            value={userDetails.name}
            onChange={(e) => setUserDetails({ ...userDetails, name: e.target.value })}
            className="border rounded-lg px-4 py-2"
            required
          />
          <input
            type="text"
            placeholder="Professional Title"
            value={userDetails.title}
            onChange={(e) => setUserDetails({ ...userDetails, title: e.target.value })}
            className="border rounded-lg px-4 py-2"
            required
          />
          <input
            type="tel"
            placeholder="Phone Number"
            value={userDetails.phone}
            onChange={(e) => setUserDetails({ ...userDetails, phone: e.target.value })}
            className="border rounded-lg px-4 py-2"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={userDetails.email}
            onChange={(e) => setUserDetails({ ...userDetails, email: e.target.value })}
            className="border rounded-lg px-4 py-2"
            required
          />
          <input
            type="text"
            placeholder="Location"
            value={userDetails.location}
            onChange={(e) => setUserDetails({ ...userDetails, location: e.target.value })}
            className="border rounded-lg px-4 py-2"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Submit Details
        </button>
      </form>
    </div>
  );
};

export default UserDetailsForm; 