# [M] MSCST incident: On the BSC network, an unknown smart contract MSCST suffered a flash loan attack, resulting in an estimated loss of approximately

## Summary
Severity: Medium
Target: MSCST
Loss: $130,000
Attack method: flash loan attack
Published: 2025-12-29
Source: https://x.com/Phalcon_xyz/status/2005518274864595002
Type: slowmist-incident

## Details
On the BSC network, an unknown smart contract MSCST suffered a flash loan attack, resulting in an estimated loss of approximately $130,000. The root cause of the exploit lies in the lack of access control (ACL) within the releaseReward() function of the MSCST contract, which allowed the attacker to manipulate the price of the GPC token in the PancakeSwap liquidity pool (address: 0x12da).
