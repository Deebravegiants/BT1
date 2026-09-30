# [H] Reentrancy via stagedFungible not cleared before external call

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23415
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Licredity::exchangeFungible, the transient stagedFungible flag is cleared only after the external call baseFungible.transfer(recipient, amountOut). If the base token supports transfer callbacks (e.g., ERC777-like hooks), the recipient can reenter while stagedFungible is still set. During that reentrancy they can call depositFungible, which relies on the staged state, and get a deposit recorded without actually performing a fresh token transfer. This does not apply to the native-asset path because _getStagedFungibleAndAmount uses msg.value.

## Recommendation
Follow checks-effects-interactions: clear the transient staged state before any external calls in exchangeFungible:
```solidity
(Fungible fungibleIn, uint256 amountIn) = _getStagedFungibleAndAmount();
uint256 amountOut;
+ assembly ("memory-safe") {
+ // clear staged fungible
+ tstore(stagedFungible.slot, 0)
+ }
// ...
assembly ("memory-safe") {
    // clear staged fungible
- tstore(stagedFungible.slot, 0)
}
```
