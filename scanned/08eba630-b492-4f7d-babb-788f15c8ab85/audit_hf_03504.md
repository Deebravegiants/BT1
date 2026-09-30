# [M] `RngRelayAuction.rngComplete

## Summary
Severity: Medium
Contest weight: 0.6067
Dataset id: 19199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the auction finalisation function that directly transfers the prize token to each winner when rngComplete() is executed. The contract assumes that the token transfer will always succeed, but it does not account for tokens that implement a blacklist feature, such as USDC. If a malicious winner adds its own address to the token’s blacklist, the safeTransfer call inside withdrawReserve reverts, causing the entire rngComplete() loop to fail. This denial‑of‑service condition occurs whenever the function is called after an auction and at least one recipient is blacklisted. As a result, no rewards are distributed, the auction cannot be marked as completed, and the funds remain locked in the prize pool. Users experience the symptom of receiving no reward despite being declared a winner; the UI may show the auction as still pending or the transaction may revert with an “InsufficientReserve” or generic transfer error. The issue was discovered during a security audit that examined the token handling logic and recognised that the contract interacts with external ERC20 tokens that may have additional transfer restrictions. It is hard to notice because most test tokens do not implement blacklisting, so standard unit tests pass. Conceptually, the bug belongs to the class of unchecked external call failures and pull‑payment misuse, where a contract pushes funds without verifying that the transfer will not revert. To remediate, the contract should adopt a claim‑based pattern: record each user’s entitled amount in a mapping and let users withdraw their rewards themselves, or at minimum wrap the transfer in a try/catch and handle failures gracefully. This eliminates the reliance on a successful push transfer and prevents a single blacklisted address from blocking the entire reward distribution, preserving protocol integrity and user expectations that a declared winner will receive their prize.

## Proof of Concept
The current implementation of `RngRelayAuction.rngComplete()` immediately transfers the `prizeToken` to the `recipient`.
    
```solidity
function rngComplete(
    uint256 _randomNumber,
    uint256 _rngCompletedAt,
    address _rewardRecipient,
    uint32 _sequenceId,
    AuctionResult calldata _rngAuctionResult
) external returns (bytes32) {
    ...
    for (uint8 i = 0; i < _rewards.length; i++) {
        uint104 _reward = uint104(_rewards[i]);
        if (_reward > 0) {
            prizePool.withdrawReserve(auctionResults[i].recipient, _reward);
            emit AuctionRewardDistributed(_sequenceId, auctionResults[i].recipient, i, _reward);
        }
    }  
}
```

```solidity
contract PrizePool is TieredLiquidityDistributor {
    function withdrawReserve(address _to, uint104 _amount) external onlyDrawManager {
        if (_amount > _reserve) {
            revert InsufficientReserve(_amount, _reserve);
        }
        _reserve -= _amount;
        _transfer(_to, _amount);
        emit WithdrawReserve(_to, _amount);
    }

    function _transfer(address _to, uint256 _amount) internal {
        _totalWithdrawn += _amount;
        prizeToken.safeTransfer(_to, _amount);
    }
}
```

There is a risk that if `prizeToken` is a `token` with a blacklisting mechanism, such as :`USDC`.  
Then `recipient` can block `rngComplete()` by maliciously entering the `USDC` blacklist.  
Since `RngAuctionRelayer` supports `AddressRemapper`, users can more simply specify blacklisted addresses via `remapTo()`

## Recommendation
Add `claims` mechanism, `rngComplete()` only record `cliamable[token][user]+=rewards`.  
Users themselves go to `claims`.
