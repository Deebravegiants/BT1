# [C] UBT-2 | Lack of Access Control

## Summary
Severity: Critical
Contest weight: 0.0416
Dataset id: 16194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a privilege escalation vulnerability caused by missing access‑control checks on two state‑changing functions that are intended to be restricted to administrators. The functions responsible for removing a budget allocation and for updating a team member's salary do not verify that the caller is an authorized admin, so any external address can invoke them. Because the contract assumes that only privileged accounts can modify financial parameters, the root cause is the absence of a require(msg.sender == admin) or similar modifier. An attacker can call the deletion function to erase an existing allocation, causing the allocated funds to become inaccessible or incorrectly reassigned, and can call the salary‑change function to set a member’s salary to an arbitrary value, including zero, which may result in loss of expected payouts. This can be exploited at any time after deployment, with no special conditions, simply by sending a transaction to the vulnerable functions. The impact includes unauthorized modification of accounting data, potential loss of funds for team members, and erosion of trust in the protocol’s financial governance. Users who rely on the contract to enforce salary guarantees may see their expected payments disappear, while the protocol’s overall integrity is compromised. The issue was identified during a manual security audit when the reviewer noted that the functions lacked any admin‑only modifier. Because the functions appear to perform critical financial updates, the missing check may not be obvious from the UI, making the bug hard to notice until an unexpected change occurs. The proper remediation is to enforce role‑based access control on all functions that modify allocations or compensation, typically by adding an admin‑only modifier or integrating OpenZeppelin’s AccessControl library. This class of bug falls under 'Missing Access Control' or 'Improper Authorization', where privileged operations are exposed to any caller, leading to unauthorized state changes and financial loss.

## Recommendation
Add a check that the msg.sender is an admin.
