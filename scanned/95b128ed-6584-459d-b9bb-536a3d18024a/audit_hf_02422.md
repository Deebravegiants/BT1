# [M] Possible Maker Signature Replay in DNTVault

## Summary
Severity: Medium
Contest weight: 0.4600
Dataset id: 13024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Sofa supports a number of built-in option-related vaults. While reviewing the option-opening logic in current vaults, we notice the use of signature-based validation. And our analysis shows current signature-based validation can be improved with the addition of maker-side nonce. To elaborate, we use the DNTVault as an example and show below the related _mint() routine. The routine allows for the agreement between maker and minter to be officially achieved. With that, there is a need to validate both minter and maker. Since the minter is the calling user, we only need to validate the maker with the maker-provided makerSignature (line 172). However, while examining the signature validation, we notice the message to sign does not include the nonce information, which indicates the maker signature may be replayed. Note this issue affects all current vaults.
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
            params.makerCollateral,
            params.makerBalanceThreshold,
            params.deadline,
            address(this)))
    ));
    (uint8 v, bytes32 r, bytes32 s) = params.makerSignature.decodeSignature();
    require(params.maker == ecrecover(digest, v, r, s), "Vault: invalid maker signature");
    // transfer makerCollateral
    COLLATERAL.safeTransferFrom(params.maker, address(this), params.makerCollateral);
    // mint product
    startDate = ((expiry - 28800) / 86400 + 1) * 86400 + 28800;
    uint256 term = (params.expiry - (((block.timestamp - 28800) / 86400 + 1) * 86400 + 28800)) / 86400;
    require(term > 0, "Vault: invalid term");
    uint256 productId = getProductId(term, params.expiry, params.anchorPrices, uint256(0));
    uint256 makerProductId = getProductId(term, params.expiry, params.anchorPrices, uint256(1));
    _mint(_msgSender(), productId, totalCollateral, "");
    _mint(params.maker, makerProductId, totalCollateral, "");
    emit Minted(_msgSender(), params.maker, referral, totalCollateral, term, params.expiry, params.anchorPrices, params.makerCollateral);
}
```

## Recommendation
Revise the above routine to add the nonce information to prevent maker signature from being replayed.
