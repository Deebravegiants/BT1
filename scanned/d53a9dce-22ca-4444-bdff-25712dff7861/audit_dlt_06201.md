# [M] After the admin address is changed, mnft sends an error.

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-13
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/52
Type: hats-finding

## Details
**Github username:** @9olidity
**Twitter username:** --
**Submission hash (on-chain):** 0x462b8f9ab5a0576bf841811fe4190adeb52ecb86969ca9c589b62007b94d5c19
**Severity:** medium

**Description:**
**Description**

After the admin address is changed, mnft sends an error.

**Attack Scenario**

```solidity
function listForSale(uint256[] calldata _mNftTokenIds, uint256[] calldata _targetTNftTokenIds, address[] calldata _reservedBuyers) external onlyAdmin {
        require(_mNftTokenIds.length == _reservedBuyers.length, "Input arrays must be the same length");
        for (uint256 i = 0; i < _mNftTokenIds.length; i++) {
            uint256 mNftTokenId = _mNftTokenIds[i];

            reservedBuyers[mNftTokenId] = _reservedBuyers[i];
            targetTNftTokenIds[mNftTokenId] = _targetTNftTokenIds[i];

            membershipNft.safeTransferFrom(msg.sender, address(this), mNftTokenId, 1, "");
        }
    }
function delist(uint256[] calldata _mNftTokenIds) external onlyAdmin nonReentrant {
        for (uint256 i = 0; i < _mNftTokenIds.length; i++) {
            uint256 tokenId = _mNftTokenIds[i];
            require(reservedBuyers[tokenId] != address(0), "Token is not currently listed for sale");

            reservedBuyers[tokenId] = address(0);
            targetTNftTokenIds[tokenId] = 0;

            membershipNft.safeTransferFrom(address(this), owner(), tokenId, 1, "");//@audit  if owner != admin
        }
    }
    function updateAdmin(address _newAdmin) external onlyOwner {
        require(_newAdmin != address(0), "Cannot be address zero");
        admin = _newAdmin;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/52_
