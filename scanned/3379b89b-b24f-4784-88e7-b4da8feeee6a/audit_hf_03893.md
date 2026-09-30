# [H] Vault: The attacker can sandwich attack him-

## Summary
Severity: High
Contest weight: 0.2071
Dataset id: 20182
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The attacker could call MarginDex to open/close positions in Vault. The swap slippage is controlled by the attacker. He can set the slippage to infinite to steal from swaps and leave a bad position/debt. In open_position of Vault, max_leverage is first checked to ensure the position that is about to open will be healthy. Then token is borrowed and swapped into position token. The attacker can set slippage to infinite and sandwich attack the swap to steal almost all of the swapped token. Then the amount swapped out is recorded in position and the position will be undercollateralized. Swaps in close_position and reduce_position are also vulnerable to this sandwich attack. The attacker can attack to steal from swap and make a bad debt. The protocol could be drained because of this sandwich attack.

## Recommendation
Call _is_liquidatable in the end of open_position and reduce_position. Check pool price deviation to oracle price inside close_position.
