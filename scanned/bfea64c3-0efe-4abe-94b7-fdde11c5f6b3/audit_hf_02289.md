# [M] Possible Mint/Burn Replay in MemefiAssetController

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 12503
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Memefi protocol has a core MemefiAssetController contract that is used to facilitate user mint/burn operations. While examining the logic to mint or burn, we notice the current implementation should be improved to defend against possible replay attacks. To elaborate, we show below the related userMint() routine. It has a rather straightforward logic in validating the given input and then minting the requested token amount. However, when successfully validating the user input, it does not mark the given nonce such that it should not be used afterward. As a result, a malicious user may repeatedly use the same given input to replay the mint operation. Note the burn operation shares the same issue.
```solidity
function userMint(
    address to,
    address assetAddress,
    AssetType assetType,
    uint256 erc1155TokenId,
    uint256 amount,
    uint256 nonce,
    uint256 deadline,
    bytes memory signature
) external {
    require(deadline >= block.timestamp, "Signature expired");
    require(!isNonceUsed[nonce], "Nonce already used");
    require(amount > 0, "Amount is 0");
    require(assetAddress != address(0), "Wrong address");
    require(assetType != AssetType.Undefined, "Asset type undefined");
    bytes32 typedHash = _hashTypedDataV4(
        keccak256(
            abi.encode(
                keccak256(
                    "Mint(address executor,address receiver,address assetAddress,uint256 assetType,uint256 erc1155TokenId,uint256 amount,uint256 nonce,uint256 deadline)"
                ),
                msg.sender,
                to,
                assetAddress,
                assetType,
                erc1155TokenId,
                amount,
                nonce,
                deadline
            )
        )
    );
    require(
        ECDSA.recover(typedHash, signature) == memefiManagement.signer(),
        "Invalid signature"
    );
    uint256[] memory mintedIds = IMemefiMintableAsset(assetAddress).assetsMint(to, amount, erc1155TokenId);
    emit Minted(
        nonce,
        msg.sender,
        to,
        assetAddress,
        amount,
        erc1155TokenId,
        mintedIds
    );
}
```

## Recommendation
Improve the above routine by adding necessary replay defense.
