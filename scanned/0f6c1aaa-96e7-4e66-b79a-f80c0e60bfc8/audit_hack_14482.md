# [M] Owner of MeritDutchAuction.sol can break minting for users

## Summary
Severity: Medium
Reporter: radev_sw
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Owner of MeritDutchAuction.sol can break minting for users

## Summary
The Owner of the `MeritDutchAuction.sol` contract can potentially break the minting process for users due to a race condition vulnerability.

## Vulnerability Detail
In the current implementation of the mint function, the value sent by the user is transferred to the contract before the sufficient funds check is performed. Since `mint()` function is marked as payable the msg.value is transferred at the moment of calling the function. This opens up a window where the contract owner can call claimProceeds() function, which drains the contract balance. If this action is executed after the user's funds are transferred but before the require check in the mint function, the `require(msg.value >= totalPaid, "Insufficient funds");` statement would revert because `msg.value` will be less than `totalPaid`.

## Impact
The vulnerability could potentially allow the contract owner to disrupt the minting process for other users, leading to failed transactions and an unreliable user experience. In the worst-case scenario, this vulnerability could erode trust in the contract and might be exploited to create unfavorable market conditions.
Another potential scenario is that while a user is minting an NFT through the MeritNFT contract, the owner of the MeritDutchAuction contract could call the claimProceeds() function, emptying the contract's balance before the minting process is complete.

Why the owner to do this:
- Immediate Profit: If the auction owner sees a large pending transaction, they could decide to claim the funds immediately rather than wait for the auction to end. This could be especially tempting if the auction is not going as well as they had hoped, or if they need immediate liquidity.
- Market Manipulation: The owner could use this exploit to manipulate the market. By disrupting large transactions, they could create uncertainty and potentially drive down the price of the NFT. This could allow them to buy more at a lower price.
- Competitive Advantage: If the owner is also a participant in the auction (or if they're colluding with a participant), they could use this exploit to disadvantage other participants and improve their own chances of winning the auction.
- Destructive Intent: If the owner has malicious intent towards the users or the platform (for example, due to a dispute or rivalry), they could use this vulnerability to disrupt operations and harm the platform's reputation.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L172-L179

## Tool used
Manual Review

## Recommendation
- A potential fix for this vulnerability would be to first ensure that the user has sent enough funds before the actual fund transfer to the contract takes place:
- Another potential fix is implementation of pause/unpause mechanism in the contract. This would allow the minting process to be paused during critical operations, preventing any interference or reentrancy attacks. This can be done by using the Pausable contract from the OpenZeppelin library. By making the minting function 'pausable', you can ensure that it cannot be interrupted by other contract calls, including the claimProceeds() function.
- It is also recommended to consistently implement the checks-effects-interactions pattern in the contract to prevent similar vulnerabilities.
