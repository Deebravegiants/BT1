# [M] Admin can prevent raffle winner from claiming prize

## Summary
Severity: Medium
Contest weight: 0.1650
Dataset id: 23129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By whitelisting their address and sending a WINNER_DRAWN CCIP message to PrizeManager, Admin can steal the raffle prize, which breaks the invariant from README:  
Winnables admins cannot do anything to prevent a winner from withdrawing their prize  
In WinnablesPrizeManager, Admin can add/remove any address as CCIP counterpart at any time.  

Internal pre-conditions  
A raffle is able to reach REQUESTED stage (enough tickets were sold).  
Attack Path  
1. Admin sends NFT (or token/ETH) to PrizeManager.  
2. Admin calls PrizeManager#lockNFT.  
3. Admin calls TicketManager#createRaffle.  
4. Raffle (ticket sale) ends successfully.  
5. drawWinner is called.  
6. Admin adds himself as PrizeManager's CCIP counterpart and sends WINNER_DRAWN CCIP message with his own address as winner to PrizeManager; Admin removes TicketManager from PrizeManager's CCIP counterparts.  
7. Chainlink VRF request from step 5 is fulfilled.  
8. TicketManager#propagate is called, which propagates Alice as the winner of the raffle, but CCIP message reverts on the destination chain with UnauthorizedCCIPSender().  
9. Admin claims reward from PrizeManager.  
Admin steals the raffle reward.

## Recommendation
Admin should not be able to add or remove CCIP counterparts during Raffles.
