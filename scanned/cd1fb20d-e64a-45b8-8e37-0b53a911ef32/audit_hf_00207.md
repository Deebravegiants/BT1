# [M] Missing `_token.approve`

## Summary
Severity: Medium
Contest weight: 0.1531
Dataset id: 1093
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[`SettToRenIbbtcZap.sol` L162-L183](https://github.com/Badger-Finance/badger-ibbtc-utility-zaps/blob/8d265aacb905d30bd95dcd54505fb26dc1f9b0b6/contracts/SettToRenIbbtcZap.sol#L162-L183)
    
    function setZapConfig(
        uint256 _idx,
        address _sett,
        address _token,
        address _curvePool,
        address _withdrawToken,
        int128 _withdrawTokenIndex
    ) external {
        _onlyGovernance();
    
        require(_sett != address(0));
        require(_token != address(0));
        require(
            _withdrawToken == address(WBTC) || _withdrawToken == address(RENBTC)
        );
    
        zapConfigs[_idx].sett = ISett(_sett);
        zapConfigs[_idx].token = IERC20Upgradeable(_token);
        zapConfigs[_idx].curvePool = ICurveFi(_curvePool);
        zapConfigs[_idx].withdrawToken = IERC20Upgradeable(_withdrawToken);
        zapConfigs[_idx].withdrawTokenIndex = _withdrawTokenIndex;
    }

In the current implementation, when `curvePool` or `token` got updated, `token` is not approved to `curvePool`, which will malfunction the contract and break minting.

## Recommendation
No recommendation
