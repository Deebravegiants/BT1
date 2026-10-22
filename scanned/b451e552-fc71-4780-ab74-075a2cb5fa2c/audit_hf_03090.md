# [M] Event emitted with incorrect value

## Summary
Severity: Medium
Contest weight: 0.1210
Dataset id: 17464
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Event PositionUpdated is always emitted with a value of PositionUpdatedType.ADJUSTED, which is incorrect for positions being opened. The check for _positionId == 0 in the emission of event PositionUpdated will always return false because _positionId is always updated to a non-zero value earlier. This would cause the PositionUpdated event emission to always say PositionUpdatedType.ADJUSTED and never PositionUpdatedType.OPENED. Frontend or offchain monitoring tools could be affected because they would never see new positions being opened but only positions being adjusted (even when they are being newly opened). This could negatively impact UI & UX to cause confusion and perhaps even a DoS vulnerability.

## Recommendation
Cache the _positionId value (to track a zero value for later event emission) or use a separate local variable instead of updating the parameter itself. This has been resolved. https://github.com/lyra-finance/lyra-protocol/blob/avalon/contracts/OptionToken.sol# Fixes the issue sufficiently.
