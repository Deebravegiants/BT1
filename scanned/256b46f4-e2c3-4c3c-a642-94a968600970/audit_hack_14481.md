# [M] Incorrect balance emitted in 'claimProceeds' function

## Summary
Severity: Medium
Reporter: 0xrobsol
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172C1-L179C6
Type: audit-issue

## Details
# Incorrect balance emitted in 'claimProceeds' function

## Summary
The claimProceeds function in the MeritDutchAuction contract emits an event after transferring the balance, which may lead to incorrect information being logged.

## Vulnerability Detail
The claimProceeds function is designed to allow the owner of the contract to claim the proceeds of the auction. After the funds are transferred to the owner, the function emits an event logging the balance of the contract. However, as the event is emitted after the balance has been transferred, it logs a balance of zero, rather than the amount that was transferred.

## Impact
This issue could mislead off-chain services and users monitoring the contract events, as it provides an incorrect representation of the actual contract balance at the time of claim. This might lead to misunderstandings or wrong calculations related to the auction's proceeds.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172C1-L179C6

## Tool used

Manual Review

## Recommendation
To address this issue, it is suggested to store the balance in a temporary variable before transferring the funds and emit this value in the event. For example:
`
function claimProceeds() external onlyOwner {
    uint256 balance = address(this).balance;
    // Send ETH to the owner
    (bool success, ) = payable(msg.sender).call{value: balance}(bytes(""));
    // Revert if transfer failed
    require(success, "Claim failed");
    // Emit event for offchain integrations
    emit ClaimedProceeds(balance);
}
`

This would ensure that the logged balance accurately represents the amount of funds transferred to the owner.
