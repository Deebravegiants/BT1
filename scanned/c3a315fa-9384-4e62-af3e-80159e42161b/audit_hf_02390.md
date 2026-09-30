# [M] Possible Cancellation Denial-of-Service in Raffle

## Summary
Severity: Medium
Contest weight: 0.4066
Dataset id: 12887
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Raffle protocol supports a number of token types as the raffle prizes, including ERC20, ERC721, ERC1155, and ETH. While examining the ERC1155-based prizes, we notice the current cancellation logic may suffer from a subtle denial-of-service issue. To elaborate, we show below the related Raffle::cancel() routine, which basically invokes the underlying _cancel() helper to return back the deposited prizes. In the prize-returning logic, we notice the raffle owner may be able to block the raffle from being cancelled when the fee token type is ERC1155. Specifially, the _cancel() helper calls the _transferPrize() routine, which makes use of _executeERC1155SafeTransferFrom() to potentially invoke the callback on the raffle owner. The callback can simply revert to block the cancellation, which essentially locks existing raffle entries.
```solidity
function cancel(uint256 raffleId) external nonReentrant {
    Raffle storage raffle = raffles[raffleId];
    RaffleStatus
```

## Recommendation
Revisit the above logic to block the denial-of-service issue on the raffle cancellation.
