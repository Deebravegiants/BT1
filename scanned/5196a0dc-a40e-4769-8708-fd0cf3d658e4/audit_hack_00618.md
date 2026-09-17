# [M] Malda incident: The vulnerability originated in the Migrator.sol contract. The contract allowed the Mendi Comptroller address to be passed dynamic

## Summary
Severity: Medium
Target: Malda
Loss: $ 285,000
Attack method: Contract Vulnerability
Published: 2025-05-30
Source: https://mirror.xyz/0x4Da818DD3aAfb9D042a76B5037cdBa61533C7692/yhFSyxCImJ23OD00vb2GQ0JmbcBkX2CO4V2t_29ykIA
Type: slowmist-incident

## Details
The vulnerability originated in the Migrator.sol contract. The contract allowed the Mendi Comptroller address to be passed dynamically, rather than being hardcoded. This enabled the attacker to supply their own malicious Comptroller, mint a synthetic position on Malda, and withdraw approximately $285,000.
