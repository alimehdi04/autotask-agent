"use client";
import { useState } from "react";

export default function InternalSystemPage() {
    const [message, setMessage] = useState("");

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);

        const payload = {
            vendor: formData.get("vendor"),
            amount: formData.get("amount"),
            due_date: formData.get("due_date"),
        };

        const res = await fetch("https://autotask-agent-tzep.onrender.com/internal-system", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            setMessage("Error 500: Database lock timeout. Please try again.");
        } else {
            const data = await res.json();
            setMessage(`Success: ${data.record_id} saved.`);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 p-10 font-sans flex flex-col items-center">
            <h1 className="text-3xl font-bold mb-6 text-white">
                Internal Entry System
            </h1>

            <form
                onSubmit={handleSubmit}
                className="bg-gray-900 p-8 rounded-lg w-full max-w-md shadow-lg"
            >
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                        Vendor Name
                    </label>
                    <input
                        name="vendor"
                        id="vendor-input"
                        required
                        className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                        Amount
                    </label>
                    <input
                        name="amount"
                        id="amount-input"
                        type="number"
                        required
                        className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
                    />
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                        Due Date
                    </label>
                    <input
                        name="due_date"
                        id="date-input"
                        type="date"
                        required
                        className="w-full bg-gray-800 border border-gray-700 rounded p-2 text-white"
                    />
                </div>

                <button
                    type="submit"
                    id="submit-btn"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors"
                >
                    Submit Record
                </button>
            </form>

            {message && (
                <div
                    id="status-message"
                    className={`mt-6 p-4 rounded w-full max-w-md text-center font-medium ${message.includes("Error")
                        ? "bg-red-900/50 text-red-400"
                        : "bg-green-900/50 text-green-400"
                        }`}
                >
                    {message}
                </div>
            )}
        </div>
    );
}