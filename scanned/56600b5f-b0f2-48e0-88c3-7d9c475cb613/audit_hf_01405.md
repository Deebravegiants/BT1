# [C] Reentrancy in StEthHyperdrive.openShort

## Summary
Severity: Critical
Contest weight: 0.2222
Dataset id: 7217
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The StethHyperdrive._deposit function contains refund logic which performs a .call to the msg.sender. When opening shorts, this _deposit with the callback happens in the middle of state updates which can be abused by an attacker. The _deposit happens after calculating the short reserves updates (_calculateOpenShort) but before applying these updates to the reserves. When the attacker receives the callback they can trade on the same curve with the same reserves a second time which allows them to get a better price execution (incurring less slippage) than a single large trade. In the proof of concept, the attacker opens half the short initially and half the short through reentrancy, and then immediately closes the total short amount for a profit, draining the pool funds.
Proof of concept

## Recommendation
Consider fixing the reentrancy in the middle of a state update. Either, remove the refund logic in _deposit and add the refund logic only at the end of openShort after all updates have been done. Alternatively, consider adding reentrancy guards to all public functions. The reentrancy flag could be in the same storage slot as the pause flag for gas efficiency.
