# [M] No validation of contract types

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/238
Type: sherlock-finding

## Details
sorrynotsorry

medium

# No validation of contract types

## Summary
AstariaRouter has no validation of contract types in the constructor
## Vulnerability Detail
AstariaRouter sets 7 addresses in the constructor.

However, non-of the contracts are validated to be in compliance with the same contract type that they're being set to.
Constructor assumes that `_COLLATERAL_TOKEN`, `_LIEN_TOKEN`, `_TRANSFER_PROXY` are in the same type of `ICollateralToken`, `ILienToken`, `ITransferProxy`, but this validation is not done by the require statements.

Since there are several core addresses set at once, it's a possibility that the addresses are shuffled or even the wrong address is set. E.g., It might be too late to discover once the deposits are made to another contract if the Vault address is set wrong like in `vault.deposit(amount, address(msg.sender))`

## Impact
Loss of user funds, re-deployment expenses
## Code Snippet
```solidity
  constructor(
    Authority _AUTHORITY,
    address _WETH,
    ICollateralToken _COLLATERAL_TOKEN,
    ILienToken _LIEN_TOKEN,
    ITransferProxy _TRANSFER_PROXY,
    address _VAULT_IMPL,
    address _SOLO_IMPL
  ) Auth(address(msg.sender), _AUTHORITY) {
    WETH = ERC20(_WETH);
    COLLATERAL_TOKEN = _COLLATERAL_TOKEN;
    LIEN_TOKEN = _LIEN_TOKEN;
    TRANSFER_PROXY = _TRANSFER_PROXY;
    VAULT_IMPLEMENTATION = _VAULT_IMPL;
    SOLO_IMPLEMENTATION = _SOLO_IMPL;
    liquidationFeePercent = 13;
    minInterestBPS = uint256(0.0005 ether) / uint256(365 days); //5 bips / second
    minEpochLength = 7 days;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/238_
