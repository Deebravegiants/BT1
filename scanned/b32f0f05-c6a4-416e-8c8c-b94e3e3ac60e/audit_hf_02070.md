# [M] BLP CooldownDuration Bypass in Liquidity Removal

## Summary
Severity: Medium
Contest weight: 0.4566
Dataset id: 11734
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BeamEx protocol has a BlpManager contract that allows the minting and redemption of BLP, the platform's liquidity provider token. We notice there is a cooldown duration after minting BLP. The cooldown duration represents the time that needs to pass for the user before it can be redeemed. Our analysis shows that this cooldown enforcement can be bypassed. To elaborate, we show below the related _removeLiquidity() routine. When the intended liquidity is requested for removal, this routine will validate the cooldown duration is passed. However, it can trivially bypassed by transferring the BLP to another new account and instructing the new account to perform the liquidity removal without further being constrained by the cooldown duration.

```solidity
function _removeLiquidity(
    address _account,
    address _tokenOut,
    uint256 _glpAmount,
    uint256 _minOut,
    address _receiver
) private returns (uint256) {
    require(_glpAmount > 0, "BlpManager: invalid _glpAmount");
    require(
        lastAddedAt[_account].add(cooldownDuration) <= block.timestamp,
        "BlpManager: cooldown duration not yet passed"
    );
    // calculate aum before sellUSDG
    uint256 aumInUsdg = getAumInUsdg(false);
    uint256 glpSupply = IERC20(blp).totalSupply();
    uint256 usdgAmount = _glpAmount.mul(aumInUsdg).div(glpSupply);
    uint256 usdgBalance = IERC20(usdg).balanceOf(address(this));
    if (usdgAmount > usdgBalance) {
        IUSDG(usdg).mint(address(this), usdgAmount.sub(usdgBalance));
    }
    IMintable(blp).burn(_account, _glpAmount);
    IERC20(usdg).transfer(address(vault), usdgAmount);
    uint256 amountOut = vault.sellUSDG(_tokenOut, _receiver);
    require(amountOut >= _minOut, "BlpManager: insufficient output");
    emit RemoveLiquidity(
        _account,
        _tokenOut,
        _glpAmount,
        aumInUsdg,
        glpSupply,
        usdgAmount,
        amountOut
    );
    return amountOut;
```

## Recommendation
Revise the BLP routine to honor the above cooldown duration as well.
