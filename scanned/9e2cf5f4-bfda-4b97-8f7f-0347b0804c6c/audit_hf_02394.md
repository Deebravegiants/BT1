# [H] Unauthorized Liquidity Addition in StableVault

## Summary
Severity: High
Contest weight: 0.6243
Dataset id: 12923
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Rollup protocol has a core StableVault contract that implements a stablecoin vault with marginal assets for the trading of perpetual derivatives. Our analysis on the related liquidity-adding logic shows a ﬂawed implementation that may be exploited to steal funds from approving users.

To elaborate, we show below the implementation of the related depositFor() helper routine. While it properly achieves the design goal in allowing users to deposit stable tokens to get the vault share, it misses the needed veriﬁcation on the caller. As a result, a malicious user may trigger the deposit for another victim user (as far as the user has approved the vault to transfer the supported funds) and the fund is sourced from the victim user. Even worse, the recipient of minted vault share may be arbitrarily speciﬁed by the malicious user. In other words, the malicious user may steal funds from approving users by eventually redeeming the vault share.

```solidity
function depositFor(
    PriceData[] calldata _priceDataList,
    bytes[] calldata _signatureList,
    address _from,
    address _token,
    uint256 _amount,
    address _receiver
) public override returns (uint256, uint256) {
    if (!allowed[_token]) revert("StableVault: token not listed");
    _checkAndSetPrice(_receiver, _priceDataList, _signatureList);
    // transfer token to vault
    IERC20(_token).transferFrom(_from, address(this), _amount);
    // convert stable token to vault unit
    uint256 _uAmount = tokenAmountToStableAmount(_token, _amount);
    uint256 _fee = _uAmount * stakeFeeBasisPoints[0] / PRECISION;
    uint256 _share = toShare(_uAmount - _fee);
    _mint(_receiver, _share);
    emit AddLiquidity(_from, _token, _amount, _share, totalSupply(), lpPrice);
    return (_share, _fee);
}
```

## Recommendation
Verify the caller of the above depositFor() routine so that only authorized entity is able to move user funds.
