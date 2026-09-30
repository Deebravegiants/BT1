# [M] Interchanged from-to addresses cause loss of user funds

## Summary
Severity: Medium
Contest weight: 0.1660
Dataset id: 17463
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The from and to addresses are interchanged in _returnBase and _returnQuote leading to an excess amount of base/quote asset in the contract being transferred again from the user (to contract) instead of being sent back to the user (from the contract). When a user closes or force closes their position via OptionMarketWrapperWithSwaps, the user's excess base assets in the contract are expected to be sent back to the user via a call to _returnBase. However, when _returnBase makes a call to _transferAsset, it incorrectly uses msg.sender as the from address and address(this) as the to address, instead of the other way around. A similar issue exists in _returnQuote, which affects both the opening and closing of positions. This leads to the loss of user funds whose excess quote/base asset while opening/closing a position is transferred again from the user to the contract leading to twice the amount of the user's initial excess base asset getting stuck in the contract.

## Recommendation
Use _transferAsset(baseAsset, address(this), msg.sender, baseBalance) in _returnBase. Use _transferAsset(inputAsset, address(this), msg.sender, quoteBalance) in _returnQuote. This has been resolved. Update: Sounds reasonable. a recent commit post-CASE-start (see https://github.com/lyra-finance/lyra-protocol/blob/0126776cc4061d66ed0400fce21d43e2eea172df/contracts/periphery/Wrapper/OptionMarketWrapperWithSwaps.sol#L458 and https://github.com/lyra-finance/lyra-protocol/blob/0126776cc4061d66ed0400fce21d43e2eea172df/contracts/periphery/Wrapper/OptionMarketWrapperWithSwaps.sol#L476).
