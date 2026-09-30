# [M] Users may lose funds when they deposit/wrap

## Summary
Severity: Medium
Contest weight: 0.5928
Dataset id: 1888
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Malicious users can increase stUSR share's price and then users who deposit/wrap funds wstUSR contract may lose their funds.
In StUSR:_convertToShares, we add 1000 share offset in the share's calculation. It means users can get 1000 share when they deposit 1 wei token. This will help prevent the inflation attack in StUSR. In WstUSR, we calculate wstUSR share's amount based on the stUSR share's price. And wstUSR share's price is 1000x stUSR share's price. This will cause that wstUSR token may face the inflation attack.
Considering below scenario:
1. Users withdraw all USR tokens from stUSR.
2. Alice deposits 1 wei USR into stUSR, 1000 stUSR shares are minted for Alice.
3. Alice donates (2000*1e18 - 1) USRs to increase stUSR share's price to 1 share --> 1e18 USR.
4. Bob wants to wrap his USR (500 * 1e18) to WstUSR. Based on current stUSR share's price, wstUSR contract should get 500 stUSR shares. When we calculate wstUSRAmount, we should divide ST_USR_SHARES_OFFSET. So the wstUSRAmount will be round down to 0. Bob will get 0 wstUSR token. Bob will lose all his money.
stUSR -->
```solidity
function _convertToShares(
    uint256 _underlyingTokenAmount,
    Math.Rounding _rounding
) internal view returns (uint256 shares) {
    return _underlyingTokenAmount.mulDiv(totalShares() + 1000,
        _totalUnderlyingTokens() + 1, _rounding);
}
```
WstUSR -->
```solidity
function previewDeposit(uint256 _usrAmount) public view returns (uint256 wstUSRAmount) {
    return IStUSR(stUSRAddress).previewDeposit(_usrAmount) / ST_USR_SHARES_OFFSET;
}

function wrap(uint256 _stUSRAmount, address _receiver) public returns (uint256 wstUSRAmount) {
    _assertNonZero(_stUSRAmount);
    wstUSRAmount = convertToShares(_stUSRAmount);
    IERC20(stUSRAddress).safeTransferFrom(msg.sender, address(this), _stUSRAmount);
    _mint(_receiver, wstUSRAmount);
    emit Wrap(msg.sender, _receiver, _stUSRAmount, wstUSRAmount);
    return wstUSRAmount;
}

function convertToShares(uint256 _usrAmount) public view returns (uint256 wstUSRAmount) {
    return IERC20Rebasing(stUSRAddress).convertToShares(_usrAmount) / ST_USR_SHARES_OFFSET;
}
```
Internal pre-conditions
N/A
External pre-conditions
stUSR contract is empty. There is no shares. Or the malicious user own most shares.
Attack Path
1. Users withdraw all USR tokens from stUSR.
2. Alice deposits 1 wei USR into stUSR, 1000 stUSR shares are minted for Alice.
3. Alice donates (2000*1e18 - 1) USRs to increase stUSR share's price to 1 share --> 1e18 USR.
4. Bob wants to wrap his USR (500 * 1e18) to WstUSR. Based on current stUSR share's price, wstUSR contract should get 500 stUSR shares. When we calculate wstUSRAmount, we should divide ST_USR_SHARES_OFFSET. So the wstUSRAmount will be round down to 0. Bob will get 0 wstUSR token. Bob will lose all his money.
Users who deposit/wrap wstUSR may lose their funds.

## Recommendation
In WstUSR, use the same decimals for wstUSR share with stUSR share.
