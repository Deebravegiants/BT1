# [H] The quantity is calculated incorrectly when

## Summary
Severity: High
Contest weight: 0.8948
Dataset id: 22787
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The quantity is calculated incorrectly when depositing ETH to weETH. The code treats the quantity of eETH shares returned by Etherfi LiquidityPool.deposit as the actual quantity of eETH, but these two quantities are not equal. The Etherfi LiquidityPool.deposit and stETH.submit functions have the same behavior, both returning shares instead of the actual token amount. The protocol handles stETH correctly, but it doesn't handle eETH correctly.

In depositEth, if _predefinedPool == PredefinedPool.weETH, _ethTOeEth will be called to get the finalAmount.

```solidity
function depositEth(uint256 _boostAmount, PredefinedPool _predefinedPool) public payable {
    if (msg.value == 0) {
        revert NoEthSent();
    }
    uint256 _finalAmount = msg.value;
    if (_predefinedPool == PredefinedPool.wstETH) {
        _finalAmount = _ethTOstEth(_finalAmount);
    } else if (_predefinedPool == PredefinedPool.weETH) {
        _finalAmount = _ethTOeEth(_finalAmount);
    }
    _depositPredefinedAsset(_finalAmount, msg.value, _boostAmount, _predefinedPool);
}
```

_ethTOeEth will call Etherfi LiquidityPool.deposit.

```solidity
function _ethTOeEth(uint256 _amount) internal returns (uint256) {
    return IeETHLiquidityPool(eETHLiquidityPool).deposit{value: _amount}(address(this));
}
```

in reality Etherfi uses mintShare and returns the amount of shares.

```solidity
function _deposit(address _recipient, uint256 _amountInLp, uint256 _amountOutOfLp) internal returns (uint256) {
    totalValueInLp += uint128(_amountInLp);
    totalValueOutOfLp += uint128(_amountOutOfLp);
    uint256 amount = _amountInLp + _amountOutOfLp;
    uint256 share = _sharesForDepositAmount(amount);
    if (amount > type(uint128).max || amount == 0 || share == 0) revert InvalidAmount();
    eETH.mintShares(_recipient, share);
    return share;
}
```

_depositPredefinedAsset is called in depositEth, which in turn called _eethTOweEth, and the parameter is the share quantity of eETH returned by _ethTOeEth.

```solidity
} else if (_predefinedPool == PredefinedPool.weETH) {
    _finalAmount = _eethTOweEth(_amount);
```

```solidity
function _eethTOweEth(uint256 _amount) internal returns (uint256) {
    return IweETH(weETH).wrap(_amount);
}
```

However, in weETH.wrap, the parameter should be the actual amount of eETH rather than the amount of shares, as there is a conversion relationship between the actual amount and the amount of shares, they are not equal.

```solidity
function wrap(uint256 _eETHAmount) public returns (uint256) {
    require(_eETHAmount > 0, "weETH: cant wrap zero eETH");
    uint256 weEthAmount = liquidityPool.sharesForAmount(_eETHAmount);
    _mint(msg.sender, weEthAmount);
    return weEthAmount;
}
```

eETH.transfer is to convert amount to share and then transferShare.

```solidity
function _transfer(address _sender, address _recipient, uint256 _amount) internal {
    convert amount to share
    _transferShares(_sender, _recipient, _sharesToTransfer);
    emit Transfer(_sender, _recipient, _amount);
}
```

As for why the current test cases pass, it is because MockEETHLiquidityPool.deposit uses eEth.mint(msg.sender, mintAmount);, which directly increases the amount of eETH and returns that amount directly, rather than returning the number of shares as in Etherfi.

```solidity
function deposit(address _referral) external payable returns (uint256) {
    _referral;
    uint256 mintAmount = msg.value / 1001 * 1000;
    eEth.mint(msg.sender, mintAmount);
    return mintAmount;
}
```

As there is a conversion rate between the amount of eETH and the number of shares, which are not equal, the following situations may occur:
• If 100 ETH is deposited, 100 eETH and 90 eETH shares are obtained, then weETH.wrap(90) is executed, 10 eETH cannot be deposited into the pool, and the user loses assets.
• If 100 ETH is deposited, 100 eETH and 110 eETH shares are obtained, then weETH.wrap(110) is executed. Since there are only 100 eETH, the transaction will revert and the user will not be able to deposit assets.

## Recommendation
Like _ethTOstEth, return the difference of eETH balance instead of directly returning the result of LiquidityPool.deposit.

```solidity
function _ethTOstEth(uint256 _amount) internal returns (uint256) {
    uint256 balanceBefore = IERC20(stETH).balanceOf(address(this));
    IstETH(stETH).submit{value: _amount}(address(this));
    return (IERC20(stETH).balanceOf(address(this)) - balanceBefore);
}
```
