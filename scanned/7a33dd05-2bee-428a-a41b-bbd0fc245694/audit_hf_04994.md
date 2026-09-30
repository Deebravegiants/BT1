# [M] Mismatch between lastValorUpdateTimestamp

## Summary
Severity: Medium
Contest weight: 0.6830
Dataset id: 22972
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
lastValorUpdateTimestamp = block.timestamp;
```
lastValorUpdateTimestamp is set to the current block.timestamp, but it is not set to the same value as valorEmissionStartTimestamp, which is set to block.timestamp + 1 days. This mismatch leads to an incorrect calculation of the valor emission. During the OmnichainLedgerV1.initialize() function, the valorEmissionStartTimestamp is set in the valorInit() function, while the lastValorUpdateTimestamp is set in the stakingInit() function. Specifically:
```solidity
valorEmissionStartTimestamp = block.timestamp + 1 days;
lastValorUpdateTimestamp = block.timestamp;
```
As a result, lastValorUpdateTimestamp is 1 day earlier than valorEmissionStartTimestamp. This mismatch leads to incorrect behavior during the first valor emission. In the Valor._getValorPendingEmission() function, the calculation of the newly emitted valor amount is based on the elapsed seconds since lastValorUpdateTimestamp. However, since lastValorUpdateTimestamp is 1 day earlier than valorEmissionStartTimestamp, the newly emitted valor amount is greater than expected, as if the emission had already started 1 day earlier.
```solidity
uint256 secondsElapsed = block.timestamp - lastValorUpdateTimestamp;
```
The mismatch also occurs in the Valor.setValorEmissionStartTimestamp() function, as it only resets the valorEmissionStartTimestamp, but does not update the lastValorUpdateTimestamp. Valor emission actually starts 1 days earlier than intended.

## Recommendation
```solidity
function stakingInit(address, uint256 _unstakeLockPeriod) internal onlyInitializing {
    unstakeLockPeriod = _unstakeLockPeriod;
    lastValorUpdateTimestamp = block.timestamp + 1 days;
}
function setValorEmissionStartTimestamp(uint256 _valorEmissionStartTimestamp) external whenNotPaused onlyRole(DEFAULT_ADMIN_ROLE) {
    if (block.timestamp > valorEmissionStartTimestamp) revert ValorEmissionAlreadyStarted();
    if (block.timestamp > _valorEmissionStartTimestamp) revert ValorEmissionCouldNotStartInThePast();
    valorEmissionStartTimestamp = _valorEmissionStartTimestamp;
    lastValorUpdateTimestamp = _valorEmissionStartTimestamp;
}
```
