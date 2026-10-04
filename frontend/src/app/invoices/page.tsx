"use client";
import { useEffect, useState } from "react";

export default function InvoicesPage() {
    const [invoices, setInvoices] = useState<any[]>([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/invoices")
            .then((res) => res.json())
            .then((data) => setInvoices(data.data));
    }, []);

    return (
        <div className="min-h-screen bg-gray-950 text-gray-100 p-10 font-sans">
            <h1 className="text-3xl font-bold mb-6 text-white">Pending Invoices</h1>
            <div className="overflow-x-auto">
                <table className="min-w-full bg-gray-900 rounded-lg overflow-hidden" id="invoice-table">
                    <thead className="bg-gray-800">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">ID</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Vendor</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Amount</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Due Date</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800">
                        {invoices.map((inv) => (
                            <tr key={inv.id} className="invoice-row">
                                <td className="px-6 py-4 whitespace-nowrap text-gray-400">{inv.id}</td>
                                <td className="px-6 py-4 whitespace-nowrap font-medium vendor-cell">{inv.vendor}</td>
                                <td className="px-6 py-4 whitespace-nowrap amount-cell">{inv.amount}</td>
                                <td className="px-6 py-4 whitespace-nowrap date-cell">{inv.due_date}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}