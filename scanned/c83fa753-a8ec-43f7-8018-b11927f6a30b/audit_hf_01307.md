# [M] `createVault`

## Summary
Severity: Medium
Contest weight: 0.6557
Dataset id: 6242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling `createVault()`, `tokenType` could be different from `token`’s type. If a user accidentally used the wrong `tokenType`, it could lead to two different results.

If `token` is an ERC20 token and the user uses `TokenType.ERC721` as `tokenType`. It is less harmful, since `ERC721(vault.token).transferFrom(msg.sender, address(this), vault.tokenIdOrAmount)` still works when `vault.token` is actually ERC20 token.

However, if `token` is an ERC721 token and the user uses `TokenType.ERC20` as `tokenType`. When doing `createVault()`, `ERC20(vault.token).safeTransferFrom(msg.sender, address(this), vault.tokenIdOrAmount)` works fine. But when doing `exercise()` or `withdraw()`, `ERC20(vault.token).safeTransfer(msg.sender, vault.tokenIdOrAmount);` doesn’t work since ERC721 doesn’t implement `safeTransfer()` function. In consequence, the ERC721 token is frozen in the vault.

## Proof of Concept
`createVault()` does not confirm whether `tokenType` and `token`’s type are the same. But the token can still be transferred into this contract. Since `transferFrom()` is implemented in ERC20 and `safeTransferFrom()` is implemented in ERC721 <https://github.com/code-423n4/2022-05-cally/blob/main/contracts/src/Cally.sol#L158-L201>

```solidity
    function createVault(
        uint256 tokenIdOrAmount,
        address token,
        uint8 premiumIndex,
        uint8 durationDays,
        uint8 dutchAuctionStartingStrikeIndex,
        uint256 dutchAuctionReserveStrike,
        TokenType tokenType
    ) external returns (uint256 vaultId) {
        require(premiumIndex < premiumOptions.length, "Invalid premium index");
        require(dutchAuctionStartingStrikeIndex < strikeOptions.length, "Invalid strike index");
        require(dutchAuctionReserveStrike < strikeOptions[dutchAuctionStartingStrikeIndex], "Reserve strike too small");
        require(durationDays > 0, "durationDays too small");
        require(tokenType == TokenType.ERC721 || tokenType == TokenType.ERC20, "Invalid token type");

        Vault memory vault = Vault({
            tokenIdOrAmount: tokenIdOrAmount,
            token: token,
            premiumIndex: premiumIndex,
            durationDays: durationDays,
            dutchAuctionStartingStrikeIndex: dutchAuctionStartingStrikeIndex,
            currentExpiration: uint32(block.timestamp),
            isExercised: false,
            isWithdrawing: false,
            tokenType: tokenType,
            currentStrike: 0,
            dutchAuctionReserveStrike: dutchAuctionReserveStrike
        });

        // vault index should always be odd
        vaultIndex += 2;
        vaultId = vaultIndex;
        _vaults[vaultId] = vault;

        // give msg.sender vault token
        _mint(msg.sender, vaultId);

        emit NewVault(vaultId, msg.sender, token);

        // transfer the NFTs or ERC20s to the contract
        vault.tokenType == TokenType.ERC721
            ? ERC721(vault.token).transferFrom(msg.sender, address(this), vault.tokenIdOrAmount)
            : ERC20(vault.token).safeTransferFrom(msg.sender, address(this), vault.tokenIdOrAmount);
    }
```

However when doing `exercise()` or `withdraw()`, it always reverts since ERC721 doesn’t implement `safeTransfer()`. The ERC721 token is frozen in the contract.

```solidity
    function exercise(uint256 optionId) external payable {
        …
        // transfer the NFTs or ERC20s to the exerciser
        vault.tokenType == TokenType.ERC721
            ? ERC721(vault.token).transferFrom(address(this), msg.sender, vault.tokenIdOrAmount)
            : ERC20(vault.token).safeTransfer(msg.sender, vault.tokenIdOrAmount);
    }

    function withdraw(uint256 vaultId) external nonReentrant {
        …
        // transfer the NFTs or ERC20s back to the owner
        vault.tokenType == TokenType.ERC721
            ? ERC721(vault.token).transferFrom(address(this), msg.sender, vault.tokenIdOrAmount)
            : ERC20(vault.token).safeTransfer(msg.sender, vault.tokenIdOrAmount);
    }
```

## Recommendation
Confirm whether `tokenType` and `token`’s type are the same in `createVault()`.

ref; <https://github.com/code-423n4/2022-05-cally-findings/issues/38>

There were a lot of reports recommending a similar change, but this is one of the few that points our a critical issue that could arise in the current state.

Although the issue only occurs when the original vault creator makes a user error, the fact that their NFT becomes unrecoverable makes this a Medium Risk concern.
