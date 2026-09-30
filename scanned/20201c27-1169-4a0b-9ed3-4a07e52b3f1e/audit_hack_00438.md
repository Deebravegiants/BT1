# [M] SKP incident: On BSC, the SKP token suffered a token-side LP balance drain + sync attack. The attacker profited approximately $212.85k in a sing

## Summary
Severity: Medium
Target: SKP
Loss: $ 212,850
Attack method: Smart Contract Vulnerability
Published: 2026-05-26
Source: https://x.com/TenArmorAlert/status/2059454844201562191
Type: slowmist-incident

## Details
On BSC, the SKP token suffered a token-side LP balance drain + sync attack. The attacker profited approximately $212.85k in a single transaction (162,854.21 USDT + 75.88 BNB). The root cause was a flaw in SKP token logic that allowed extra SKP tokens to be transferred out from the Pancake V2 SKP/USDT LP after a large buy, followed by calling sync() to write incorrect reserves, pushing the SKP reserve close to zero. The attacker used flash loans to amplify the attack.
