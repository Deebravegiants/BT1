# [H] Managed veAERO NFT can be withdrawn by owner after being used as collateral

## Summary
Severity: High
Contest weight: 0.3714
Dataset id: 1854
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Internal pre-conditions  
External pre-conditions  
Attack Path  
Instance 1  
The Aerodrome's veAERO NFT can be an unmanaged veNFT OR managed veNFT. A managed veAERO NFT (also called (m)veAERO NFT) operates like a vault that allows users to deposit and withdraw their unmanaged veNFT into the managed veNFT via the Voter.depositManaged and Voter.withdrawManaged functions. Thus, the locked amount within the (m)veAERO NFT can increase or decrease.  
Bob, the malicious user, owns a (m)veAERO NFT and locks his unmanaged veNFT worth 1,000,000 AERO within it. He then converts it into an NFT receipt and uses it as collateral in his borrow offer. The borrow offer intends to exchange borrow 1,000,000 USDC at the price/ratio of 1 AERO = 1 USDC.  
Bob then matches his borrow order against other users' lending orders via the permissionless DebitaV3Aggregator.matchOffersV3 function himself. A new Loan contract is created, and 1,000,000 USDC is sent to Bob's wallet, and the (m)veAERO NFT is transferred into the Loan contract.  
Next, Bob calls the Voter.withdrawManaged function to withdraw his unmanaged veNFT, which is worth 1,000,000 AERO, from the (m)veAERO NFT. As a result, the (m)veAERO NFT collateral within the Loan becomes worthless now.  
Bob now holds 1,000,000 USDC and 1,000,000 AERO.  
Bob defaults on the Loan, and the (m)veAERO NFT will be auctioned. Since the (m)veAERO NFT is worthless, no one will purchase it, and the lender will not get any funds back and will lose 1,000,000 USDC.  

Instance 2  
Any mechanism that relies on NFT receipt will be vulnerable to such an issue by exploiting the managed veNFT.  
Another instance that is affected by a similar issue is the BuyOrder.sellNFT function, where the NFT receipt with managed veNFT is placed within a buy order and put up for sale. Once the NFT receipt is sold, the seller can proceed to withdraw all the locked amount within the NFT receipt, leaving the buyer with a worthless NFT receipt. Since the root cause is similar, the attack path will be omitted for brevity.  
High. Loss of assets for lenders and buyers.

## Recommendation
No recommendation available
