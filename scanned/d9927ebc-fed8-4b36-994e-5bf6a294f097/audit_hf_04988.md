# [H] Valor._doValorEmission() should not be a pub-

## Summary
Severity: High
Contest weight: 0.8941
Dataset id: 22961
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Valor._doValorEmission() function is public, meaning it can be called by anyone. If _doValorEmission() is invoked outside of the Staking.updateValorVars() function, it can lead to the accValorPerShareScaled value being incorrectly updated when updateValorVars() is subsequently called. The _doValorEmission() function updates totalValorEmitted and lastValorUpdateTimestamp. However, since _doValorEmission() is a public function, it can be called by anyone, which could lead to unintended updates to these values. https://github.com/OrderlyNetwork/omnichain-ledger/tree/fb0c093da7876968794f6b3a93adcc23b2f81077/omnichain-ledger/contracts/lib/Valor.sol#L127-L133
```solidity
function _doValorEmission() public whenNotPaused returns (uint256 valorEmitted) {
    valorEmitted = _getValorPendingEmission();
    if (valorEmitted > 0) {
        totalValorEmitted += valorEmitted;
        lastValorUpdateTimestamp = block.timestamp;
    }
}
```
If _doValorEmission() is called outside of the Staking.updateValorVars() function, it can affect the calculation of accValorPerShareScaled, potentially leading to incorrect updates to this value. https://github.com/OrderlyNetwork/omnichain-ledger/tree/fb0c093da7876968794f6b3a93adcc23b2f81077/omnichain-ledger/contracts/lib/Staking.sol#L114-L119
```solidity
function updateValorVars() public whenNotPaused {
    uint256 valorEmission = _doValorEmission();
    if (valorEmission > 0) {
        accValorPerShareScaled = _getCurrentAccValorPerShareScaled(valorEmission);
    }
}
```
A malicious user could exploit the interplay between the _doValorEmission() and updateValorVars() functions to indefinitely prevent the growth of accValorPerShareScaled. This could be done by calling _doValorEmission() immediately before updateValorVars() is invoked, which occurs every time staking balances change. Such an attack would lead to users receiving substantially less VALOR tokens than anticipated. Users may receive significantly less VALOR tokens than they expect.

## Recommendation
The Valor._doValorEmission() function should be a internal function.
```solidity
function _doValorEmission() internal whenNotPaused returns (uint256 valorEmitted) {
    valorEmitted = _getValorPendingEmission();
    if (valorEmitted > 0) {
        totalValorEmitted += valorEmitted;
        lastValorUpdateTimestamp = block.timestamp;
    }
}
```
