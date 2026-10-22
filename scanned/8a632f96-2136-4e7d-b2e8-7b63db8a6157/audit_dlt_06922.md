# [H] `setGuardian()` Wrong implementation

## Summary
Severity: High
Chain: Smart contract
Component: 2021-11-badgerzaps
Published: 2021-11-16
Source: https://github.com/code-423n4/2021-11-badgerzaps-findings/issues/51
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

https://github.com/Badger-Finance/badger-ibbtc-utility-zaps/blob/6f700995129182fec81b772f97abab9977b46026/contracts/IbbtcVaultZap.sol#L116-L119

```solidity=116
function setGuardian(address _guardian) external {
    _onlyGovernance();
    governance = _guardian;
}
```

https://github.com/Badger-Finance/badger-ibbtc-utility-zaps/blob/a5c71b72222d84b6414ca0339ed1761dc79fe56e/contracts/SettToRenIbbtcZap.sol#L130-L133

```solidity=130
function setGuardian(address _guardian) external {
    _onlyGovernance();
    governance = _guardian;
}
```

`governance = _guardian` should be `guardian = _guardian`.
