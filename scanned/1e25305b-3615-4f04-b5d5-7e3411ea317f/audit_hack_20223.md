# [H] 5.2.7 The vault manager has unchecked power to create arbitrage usingsetSwapFees

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** AeraVaultV1.sol#L663-L679, BasePool.sol#L58-L
**Description:** A previously known issue was that a malicious vault manager could arbitrage the vault like in the
below scenario:

1. Set the swap fees to a high value bysetSwapFee(10% is the maximum).
2. Wait for the market price to move against the spot price.
3. In the same transaction, reduce the swap fees to ~0 (0.0001% is the minimum) and arbitrage the vault.
The proposed fix was to limit the percentage change of the swap fee to a maximum ofMAXIMUM_SWAP_FEE_-
PERCENT_CHANGEeach time. However, because there is no restriction on how many times thesetSwapFeefunction
can be called in a block or transaction, a malicious manager can still call it multiple times in the same transaction
and eventually set the swap fee to the value they want.
**Recommendation:** Enforce a cooldown period of reasonable length between two consecutivesetSwapFeefunc-
tion calls.
