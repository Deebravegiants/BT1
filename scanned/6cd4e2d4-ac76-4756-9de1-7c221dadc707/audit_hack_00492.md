# [M] EIP-7702 Victim incident: A user EOA on BNB Chain (with EIP-7702 delegation) that had set delegated code via an EIP-7702 Type-4 transaction was drained for

## Summary
Severity: Medium
Target: EIP-7702 Victim
Loss: $ 17,200
Attack method: Smart Contract Vulnerability
Published: 2026-04-03
Source: https://blocksec.com/blog/weekly-web3-security-incident-roundup-mar-30-apr-5-2026
Type: slowmist-incident

## Details
A user EOA on BNB Chain (with EIP-7702 delegation) that had set delegated code via an EIP-7702 Type-4 transaction was drained for ~$17.2K. The delegated code included a pancakeV3SwapCallback() function without proper access control. The attacker directly called this callback with crafted calldata, forcing the victim account to transfer its tokens to an attacker-controlled address. The victim had enabled the delegation to support swap-related logic.
