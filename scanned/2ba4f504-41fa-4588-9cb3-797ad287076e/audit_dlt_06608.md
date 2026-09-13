# [H] missing !claimed check in NATIVE `claimWithdrawal()` function

## Summary
Severity: High
Chain: Smart contract
Component: OLD-Accumulated-finance
Published: 2024-09-02
Source: https://github.com/hats-finance/OLD-Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/19
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xabd55c24fa6ef983a1bb8b977bcaea6590d1546788a87a48102e26a0cc1d3095
**Severity:** high

**Description:**
**Description**\
in the contract `minter.sol` and contract `NativeMinterWithdrawal` and `claimwithdrawal` L2126 which  is going to claim the withdrawals with native token

```solidity 
  function claimWithdrawal(uint256 withdrawalId, address receiver) public virtual nonReentrant {
        require(ownerOf(withdrawalId) == msg.sender, "NotOwner");
        WithdrawalRequest storage request = _withdrawalRequests[withdrawalId];
        require(request.processed, "NotProcessedYet");
        _burn(withdrawalId);
        request.claimed = true;
        totalUnclaimedWithdrawals = totalUnclaimedWithdrawals-request.amount;
        SafeTransferLib.safeTransferETH(receiver, request.amount);
        emit ClaimWithdrawal(address(msg.sender), receiver, request.amount, withdrawalId);
    }
```
sets the status to claimed but doesnt check that doesnt actually require that status should be `!Claimed`

like in the L2170 `claimWithdrawal` erc20 which DOES check that it should not be claimed but native one doesnt 
erc20 one: `require(!request.claimed, "AlreadyClaimed");`
as you see its fixed in the erc20 one but in the native one issue STILL REMAINS 


**Recommendation**
- consider modifying function to the way that it actually checks user claimed or not otherwise its possibe to reclaim
