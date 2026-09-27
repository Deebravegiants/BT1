# [H] Paraluni incident: The metaverse financial project Paraluni on the BSC chain was hacked, and the hackers made more than $1.7 million in profits. The

## Summary
Severity: High
Target: Paraluni
Loss: $ 1,700,000
Attack method: Reentrancy Attack
Published: 2022-03-13
Source: https://twitter.com/peckshield/status/1502815435498176514
Type: slowmist-incident

## Details
The metaverse financial project Paraluni on the BSC chain was hacked, and the hackers made more than $1.7 million in profits. The problem lies in the depositByAddLiquidity method of the MasterCheif contract of the project side. This method does not check whether the token array parameter address[2] memory _tokens matches the LP pointed to by the pid parameter, and does not add lock when the LP amount changes.
