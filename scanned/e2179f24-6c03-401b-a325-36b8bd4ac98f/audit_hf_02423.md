# [M] Possible Costly Vault Share From Improper Initialization

## Summary
Severity: Medium
Contest weight: 0.4627
Dataset id: 13026
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, Sofa supports a number of built-in option-related vaults. In the process of examining certain Aave-related vaults, we notice the share calculation for minting users and the share calculation may lead to an issue that unnecessarily makes the share extremely expensive (and brings hurdles or even causes loss for later minting users). To elaborate, we show below the _mint() routine from AAVEDNTVault. The issue occurs when the Vault is being initialized under the assumption that the current vault is empty.
```solidity
function _mint(uint256 totalCollateral, MintParams memory params, address referral) internal {
    require(block.timestamp < params.deadline, "Vault: deadline");
    require(block.timestamp < params.expiry, "Vault: expired");
    require(expiry must be 8:00 UTC);
    require(params.expiry % 86400 == 28800, "Vault: invalid expiry");
    require(params.anchorPrices[0] < params.anchorPrices[1], "Vault: invalid strike prices");
    require(params.makerBalanceThreshold <= COLLATERAL.balanceOf(params.maker), "Vault: invalid balance threshold");
    require(referral == _msgSender(), "Vault: invalid referral");
    // verify maker's signature
    bytes32 digest = keccak256(abi.encodePacked(
        "\x19\x01",
        DOMAIN_SEPARATOR,
        keccak256(abi.encode(MINT_TYPEHASH,
            _msgSender(),
            totalCollateral,
            params.expiry,
            keccak256(abi.encodePacked(params.anchorPrices)),
            params.collateralAtRisk,
            params.makerCollateral,
            params.makerBalanceThreshold,
            params.deadline,
            address(this)))
    ));
    (uint8 v, bytes32 r, bytes32 s) = params.makerSignature.decodeSignature();
    require(params.maker == ecrecover(digest, v, r, s), "Vault: invalid maker signature");
    // transfer makerCollateral
    COLLATERAL.safeTransferFrom(params.maker, address(this), params.makerCollateral);
    // calculate aToken shares
    uint256 term;
    uint256 collateralAtRiskPercentage;
    uint256 aTokenShare;
    POOL.supply(address(COLLATERAL), totalCollateral, address(this), REFERRAL_CODE);
    uint256 aTokenBalance = ATOKEN.balanceOf(address(this));
    if (totalSupply > 0) {
        aTokenShare = totalCollateral * totalSupply / (aTokenBalance - totalCollateral);
    } else {
        aTokenShare = totalCollateral;
    }
    totalSupply += aTokenShare;
}
```
Specifically, when the vault is being initialized, the shares value directly takes the value of totalCollateral (line 205), which is manipulatable by the malicious actor. As this is the first time to deposit, the totalSupply equals the given input amount. With that, the actor can further donate a huge amount to the vault (via the onBehalfOf support in Aave) with the goal of making the aTokenShare extremely expensive (line 203). An extremely expensive vault can be very inconvenient to use. Furthermore, it can lead to precision issue in truncating the computed aTokenShare for deposited assets (line 203). If truncated to be zero, the deposited assets are essentially considered dust and kept by the contract without returning back to the user.

## Recommendation
Revise current execution logic of _mint() to defensively calculate the share amount when the vault is being initialized. An alternative solution is to ensure guarded launch that safeguards the first deposit to avoid being manipulated.
