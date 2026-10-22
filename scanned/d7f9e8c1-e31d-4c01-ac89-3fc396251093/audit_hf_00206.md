# [H] `setGuardian`

## Summary
Severity: High
Contest weight: 0.1704
Dataset id: 1091
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`IbbtcVaultZap.sol` L116-L119](https://github.com/Badger-Finance/badger-ibbtc-utility-zaps/blob/6f700995129182fec81b772f97abab9977b46026/contracts/IbbtcVaultZap.sol#L116-L19)
    
    function setGuardian(address _guardian) external {
        _onlyGovernance();
        governance = _guardian;
    }

[`SettToRenIbbtcZap.sol` L130-L133](https://github.com/Badger-Finance/badger-ibbtc-utility-zaps/blob/a5c71b72222d84b6414ca0339ed1761dc79fe56e/contracts/SettToRenIbbtcZap.sol#L130-L133)
    
    function setGuardian(address _guardian) external {
        _onlyGovernance();
        governance = _guardian;
    }

`governance = _guardian` should be `guardian = _guardian`.

## Recommendation
No recommendation
