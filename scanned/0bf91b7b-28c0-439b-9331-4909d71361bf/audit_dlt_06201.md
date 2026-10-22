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
    }

modifier onlyAdmin() {
        require(msg.sender == admin, "Caller is not the admin");
        _;
    }
```


When the `admin` address is updated, if the `original admin` calls the `listForSale()` function to send mnft to the contract address before the update, and then the `new admin` calls the `delist()` function to cancel the above transaction, mnft will be sent to the contract. The owner (owner), not the `original admin`.
This is because in the `delist()` function, mnft will be sent to the owner() address through `membershipNft.safeTransferFrom`, and the `owner()` function returns the owner address of the contract, not the `original admin` address.


**Attachments**

1. **Proof of Concept (PoC) File**

- adminA call listForSale(mNftTokenId = 1)
- owner call updateAdmin(adminB)
- adminB call delist(mNftTokenId = 1)
- mNftTokenId = 1 transfer owner address

2. **Revised Code File (Optional)**

it is recommended to send MNFT to the original administrator address in the delist function instead of the owner address of the contract. You can add a variable to the contract to store the administrator address and use the address in the delist function for transfer instead of directly using the address returned by the owner() function.
