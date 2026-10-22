# [M] Inaccurate haircut Decimal Used in quotePotentialSwap()

## Summary
Severity: Medium
Contest weight: 0.4591
Dataset id: 13412
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In Wombat protocol, the Pool contract provides a quotePotentialSwap() function for users to get the maximum output token amount and the haircut for a potential swap. While examining the logic to calculate the maximum output token amount and the haircut, we notice the existence of using inaccurate decimal to convert the haircut. To elaborate, we show below the code snippet of the quotePotentialSwap() routine. As the name indicates, it provides quote for a potential swap which is given by three parameters. The ﬁrst parameter (i.e. fromToken) is the token that the user wants to provide for the swap, and the second parameter (i.e. toToken) is the token that the user wants to receive from the swap. The last parameter (i.e. fromAmount) gives the amount of the fromToken the user want to provide for the swap. Specially, if the fromAmount < 0, it is a reverse quote where the last parameter (i.e. fromAmount) gives the amount of the fromToken the user want to receive from the swap. Accordingly, the ﬁrst parameter (i.e. fromToken) is the target token that the user wants to receive and the second parameter (i.e. toToken) is the token that the user wants to provide in the swap. In the case of reverse quote, the haircut is charged in the fromToken. So the haircut needs to be converted from WAD to the decimal of the fromToken. The current haircut conversion from WAD to the decimal of the toToken (line 866) is inaccurate which needs to be ﬁxed.
```solidity
* @notice
Given an input asset amount and token addresses, calculates the
* maximum output token amount (accounting for fees and slippage).
* @dev To be used by frontend
* @param fromToken The initial ERC20 token
* @param toToken The token wanted by user
* @param fromAmount The given input amount
* @return potentialOutcome The potential amount user would receive
* @return haircut The haircut that would be applied
function quotePotentialSwap(
    address fromToken,
    address toToken,
    int256 fromAmount
) public view override returns (uint256 potentialOutcome, uint256 haircut) {
    _checkSameAddress(fromToken, toToken);
    if (fromAmount == 0) revert WOMBAT_ZERO_AMOUNT();
    IAsset fromAsset = _assetOf(fromToken);
    IAsset toAsset = _assetOf(toToken);
    fromAmount = fromAmount.toWad(fromAsset.underlyingTokenDecimals());
    (potentialOutcome, haircut) = _quoteFrom(fromAsset, toAsset, fromAmount);
    potentialOutcome = potentialOutcome.fromWad(toAsset.underlyingTokenDecimals());
    haircut = haircut.fromWad(toAsset.underlyingTokenDecimals());
}
```

## Recommendation
Correct the haircut decimal in the case of reverse quote.
