# [M] Users Unable to Claim Removed Tokens Due to Transfer Failures in claimRemovedTokens Function

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-22
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/60
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x2a60e4e670f79bb68f964cd50c776c60f0a87c58f61272a1ec41950ee8dbcd2e
**Severity:** medium

**Description:**
**Description**\
The `claimRemovedTokens` function is designed to allow users to claim their share of tokens that have been removed in previous snapshots. The function iterates over all snapshot IDs from the last claimed ID to the current snapshot ID, attempting to claim the user's share of each removed token using the `attemptClaim` function. The `safeTransfer` function within `attemptClaim` is used to transfer the calculated share to the user. If the transfer fails for any reason, the entire `claimRemovedTokens` function reverts, preventing the user from claiming any of their removed tokens.

Here is the relevant portion of the code for the `claimRemovedTokens` function:

```solidity
function claimRemovedTokens(address user) external override nonReentrant {
    if (user == address(0)) revert ErrorLibrary.InvalidAddress();
    uint256 _currentId = _currentSnapshotId;
    if (_currentId < 2) revert ErrorLibrary.NoTokensRemoved();
    uint256 lastClaimedUserId = lastClaimedRemovedTokenId[user];
    uint256 _balanceOfLastValidId;

    for (uint256 id = lastClaimedUserId + 1; id < _currentId; id++) {
        uint256 totalSupply = totalSupplyRecord[id];
        address currentRemovedToken = removedToken[id].token;
        uint256 tokenBalanceAtRemoval = removedToken[id].balanceAtRemoval;
        UserRecordData memory userData = userRecord[user][id];

        if (userData.hasInteractedWithId) {
            _balanceOfLastValidId = userData.portfolioBalance;
            delete userRecord[user][id];
        }

        attemptClaim(currentRemovedToken, user, _balanceOfLastValidId, tokenBalanceAtRemoval, totalSupply);
    }

    if (!userRecord[user][_currentId].hasInteractedWithId) {
        _setUserRecord(user, _balanceOfLastValidId);
    }

    _setLastClaimedId(user, _currentId - 1);
    emit UserClaimedToken(user, _currentId - 1);
}

function attemptClaim(
    address _removedToken,
    address _user,
    uint256 _portfolioTokenBalance,
    uint256 _balanceAtRemoval,
    uint256 _totalSupply
) private {
    if (_portfolioTokenBalance > 0) {
        uint256 balance = (_balanceAtRemoval * _portfolioTokenBalance) / _totalSupply;
        TransferHelper.safeTransfer(_removedToken, _user, balance);
    }
}

function safeTransfer(
    address token,
    address to,
    uint256 value
) internal {
    (bool success, bytes memory data) = token.call(abi.encodeWithSelector(0xa9059cbb, to, value));
    require(
        success && (data.length == 0 || abi.decode(data, (bool))),
        'TransferHelper::safeTransfer: transfer failed'
    );
}
```

This issue results in inefficiencies and potential user dissatisfaction. Users will be unable to claim their removed tokens if any single transfer operation fails, leading to potential loss of funds and a poor user experience.

**Scenario Overview**
1. **User Stakes Tokens**: A user stakes tokenA, tokenB, and tokenC in the protocol.

2. **Protocol Removes Tokens**: The protocol subsequently calls `removePortfolioToken` for tokenB and tokenC.

3. **Initiate Claim Process**: The user calls the `claimRemovedTokens` function to claim their removed tokens (tokenB and tokenC).

4. **Trigger Transfer Failure for TokenB**: During the claim process, the protocol first attempts to transfer tokenB to the user. However, the transfer of tokenB fails due to a malfunctioning token contract, insufficient balance in the contract, or any other reason.

5. **Function Reverts**: The `safeTransfer` function fails and reverts, causing the entire `claimRemovedTokens` function to revert. As a result, the user is unable to claim both tokenB and tokenC, even though the transfer of tokenC would have succeeded.

6. **Continued Transfer Failures**: If the issue with the tokenB transfer persists, the user will continuously be unable to retrieve both tokenB and tokenC every time they attempt to call the `claimRemovedTokens` function.

#### Consequences
- **Denial of Service**: The user is unable to claim any of their removed tokens due to the failure of the transfer for tokenB.
- **Potential Financial Loss**: Users might face financial losses if they are unable to reclaim valuable tokens that have been removed.



**Attachments**

1. **Proof of Concept (PoC) File**

2. **Revised Code File (Optional)**
  
**Files:**
  - revised_code.sol (https://hats-backend-prod.herokuapp.com/v1/files/Qmb4xWY6dM782NcMVqQLqnfTrjt42J3daMjyvokXKSAi7C)
  - PoC.sol (https://hats-backend-prod.herokuapp.com/v1/files/QmQ6Mrrdbu96e4YNUbVNNmM7AXVFJM8EtdfEdSZt7MCtqr)
