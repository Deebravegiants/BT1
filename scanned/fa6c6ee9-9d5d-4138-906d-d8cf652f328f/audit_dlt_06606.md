# [M] User can reject the `withdrawalId` due to use of `_safeMint()` in `requestWithdrawal()` function

## Summary
Severity: Medium
Chain: Smart contract
Component: OLD-Accumulated-finance
Published: 2024-09-02
Source: https://github.com/hats-finance/OLD-Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/27
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x5529151e09b33810031083f111e067ffb0d1a1e92844738f22635f16497c35a2
**Severity:** medium

**Description:**
**Description**\
`Mintersol` has `requestWithdrawal()` function where the user can request his base token withdrawal which is provided with redeem free management. Its implemented as:

```solidity
    function requestWithdrawal(uint256 amount, address receiver) public nonReentrant {
        require(amount >= minWithdrawal, "LessThanMin");
        uint256 netAmount = previewWithdrawal(amount);
        stakingToken.safeTransferFrom(msg.sender, address(this), amount);

        uint256 withdrawalId = nextWithdrawalId++;
@>        _safeMint(receiver, withdrawalId);

        _withdrawalRequests[withdrawalId] = WithdrawalRequest({
            amount: netAmount,
            processed: false,
            claimed: false
        });

        totalPendingWithdrawals = totalPendingWithdrawals+netAmount;
        totalWithdrawalFees = totalWithdrawalFees+amount-netAmount;

        emit RequestWithdrawal(address(msg.sender), receiver, amount, withdrawalId);
    }
```

When the user requests for his withdrawal, they would first need to transfer the stakingTokens to contract. After that  via safeMint(), a a NFT with incremented withdrawal id from previously minted NFT would be minted to user/receiver address.

`_safeMint()` is particularly used here to check the successful receival of NFT to contract address. However, `requestWithdrawal()` function can be exploited via `_safeMint()` function something similar to `ShiUniverse` incident.

Reference past attack with the use of openzeppelin's `_safeMint()` function- https://servrox-solutions.notion.site/Shi-Universe-Incident-03-07-2024-bc36aeb1124d4644b7e5342f299eca0c

The vulnerability can be arised with the use of `_safeMint` function, which is validates whether the recipient of an NFT is a smart contract. This function also checks if the smart contract has successfully received the NFT. This ensures that NFTs are not accidentally sent to non-existing or invalid contracts. However, There can be an exploit where the receiving smart contract could deliberately decline the reception of the NFT, causing the transaction to revert.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/OLD-Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/27_
