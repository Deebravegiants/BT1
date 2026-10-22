# [M] Proper Minimum Balance Enforcement

## Summary
Severity: Medium
Contest weight: 0.4596
Dataset id: 12545
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function withdraw(uint256 _shares, address _exposure, uint256 _withdrawType) public nonReentrant {
    uint256 _balShare = balanceOf(msg.sender);
    require(_validExposureTokens[_exposure], !invalidExposureToken);
    require(_balShare >= _shares, !invalidWithdrawShare);
    uint256 _stablecoinAmt = amountOfTokenForShare(msg.sender, address(token), _shares);
    uint256 _exposureAmt = amountOfTokenForShare(msg.sender, _exposure, _shares);
    // burn share
    _burn(msg.sender, _shares);
    // ensure the remaining share (denominated stablecoin value) in acceptable range
    uint256 minBal = exposureMinBalances[_exposure];
    if (minBal > 0) {
        require(_balShare >= minBal || _balShare == 0, !minAllowedBalance);
        // get required asset for withdrawal from yield farming necessary
        if (_stablecoinAmt > 0) {
            uint256 _bal = token.balanceOf(address(this));
            if (_stablecoinAmt > _bal) {
                require(yieldVaults[msg.sender][address(token)] != address(0), !invalidYieldVault);
                _yieldFarmingWithdraw(msg.sender, address(token), yieldVaults[msg.sender][address(token)], _stablecoinAmt.sub(_bal));
            }
        }
        if (_exposureAmt > 0) {
            uint256 _bal = IERC20(_exposure).balanceOf(address(this));
            if (_exposureAmt > _bal) {
                require(yieldVaults[msg.sender][_exposure] != address(0), !invalidYieldVaultExposure);
                _yieldFarmingWithdraw(msg.sender, _exposure, yieldVaults[msg.sender][_exposure], _exposureAmt.sub(_bal));
            }
        }
        uint256 markPrice = getMarkPrice(_exposure);
        if (_withdrawType == 0) {
            uint256 delta = _swapInDex(_exposure, address(token), _exposureAmt, markPrice, true);
            _stablecoinAmt = _stablecoinAmt.add(delta);
            _exposureAmt = 0;
        } else if (_withdrawType == 1) {
            uint256 delta = _swapInDex(address(token), _exposure, _stablecoinAmt, markPrice, false);
            _exposureAmt = _exposureAmt.add(delta);
            _stablecoinAmt = 0;
        }
        // update balances
        tokenBalances[msg.sender][_exposure] = tokenBalances[msg.sender][_exposure].mul(_balShare.sub(_shares)).div(_balShare);
        exposureBalances[msg.sender][_exposure] = exposureBalances[msg.sender][_exposure].mul(_balShare.sub(_shares)).div(_balShare);
        // withdrawal to user
        if (_stablecoinAmt > 0) {
            uint256 _tBal = token.balanceOf(address(this));
            token.safeTransfer(msg.sender, _stablecoinAmt > _tBal ? _tBal : _stablecoinAmt);
        }
        if (_exposureAmt > 0) {
            uint256 _eBal = IERC20(_exposure).balanceOf(address(this));
            IERC20(_exposure).safeTransfer(msg.sender, _exposureAmt > _eBal ? _eBal : _exposureAmt);
        }
        emit Withdraw(msg.sender, _exposure, _stablecoinAmt, _exposureAmt, markPrice, _shares);
    }
```
The withdraw logic requires calculating the assets owned by the user, burning the share of the user, updating the balances of the user, and transferring tokens back to the user. It comes to our attention that the current implementation does not properly honor the minimum balance requirement (line 82). The actual balance needs to be retrieved for minimum balance enforcement, instead of using the current stale balance (_balShare).

## Recommendation
Properly enforce the minimal balance requirement in the above withdraw() function.
