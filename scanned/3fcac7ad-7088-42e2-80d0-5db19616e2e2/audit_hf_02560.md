# [H] ValueCanBeExtractedFromThePoolByCombiningTheBurning of bToken and the Buying/Selling of Portal Energy

## Summary
Severity: High
Contest weight: 0.6394
Dataset id: 13722
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Value can be extracted from the pool by combining the burning of bToken and the buying/selling of portal energy. Users can profit from the liquidity in the pool. Attack Scenario A user who has provided liquidity to the virtualLP in PSM tokens via contributeFunding gets minted bToken. They can then call burnBtokens later when the pool is active to get back the PSM tokens and burn up their bToken. However, the current amount of PSM tokens in the pool contract determines the price at which portal energy can be bought/sold as seen in the quoteBuyPortalEnergy function. File: src/V2MultiAsset/PortalV2MultiAsset.sol#L672-L690
```solidity
function quoteBuyPortalEnergy(
    uint256 _amountInputPSM
) public view activeLP returns (uint256 amountReceived) {
    // @dev Calculate the PSM token reserve (input)
    uint256 reserve0 = IERC20(PSM_ADDRESS).balanceOf(VIRTUAL_LP);
    // @dev Calculate the reserve of portalEnergy (output)
    uint256 reserve1 = CONSTANT_PRODUCT / reserve0;
    // @dev Reduce amount by the LP Protection Hurdle to prevent sandwich attacks
    _amountInputPSM = (_amountInputPSM * (100 - LP_PROTECTION_HURDLE)) / 100;
    // @dev Calculate the amount of portalEnergy received based on the amount of PSM tokens sold
    amountReceived = (_amountInputPSM * reserve1) / (_amountInputPSM + reserve0);
}
```
So a user can burn their bToken to take out PSM tokens from the contract. This leads to a drop in the price of portal energy, as the PSM balance in the contract will drop. So a user can sell portal energy from the pool before, and then buy it immediately after for profit. Proof of Concept (PoC) Users can exploit it in the following way.

1. Assume the user has acquired a large number of bToken.

2. Assume the pool has 100 PSM tokens, and the CONSTANT_PRODUCT is set to 1e4.

3. The user sells the 120 portal energy tokens for 54 PSM tokens (assuming 0 LP_PROTECTION_HURDLE). Pool now has 46 PSM tokens.

4. User burns up their bToken to remove 20 PSM tokens from the pool. Pool now has only 26 PSM tokens.

5. The user buys portal energy using the 54 PSM tokens and gets back 259.6 portal energy. The user has made a profit of 139.6 portal energy. The protocol tries to mitigate this with an LP_PROTECTION_HURDLE factor. However, this is only a percentage change on the amount of tokens being exchanged. The profitability also depends on the amount of liquidity removed from the pool by burning bToken. So if a large amount of bToken can be acquired and burnt, the LP_PROTECTION_HURDLE factor becomes irrelevant.

## Recommendation
Limit the amount of bToken that can be burnt in one go. A limit for bToken burnt which replenishes over time so that users cannot manipulate the pool too much would prevent the exploit combined with the LP_PROTECTION_HURDLE factor.
