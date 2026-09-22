# [H] Hope Finance exploit: $1.86M was stolen from Hope Finance on Monday

## Summary
Severity: High
Target: Hope Finance
Loss: $1,860,000
Published: 02/20/2023
Source: https://rekt.news/hope-finance-rekt
Type: rekt-postmortem

## Details
## Hope Finance - REKT

 Wednesday, February 22, 2023 Hope Finance - Rugpull - REKT 

 read this article also in : zh 

 Abandon Hope all ye who enter here. 

 $1.86M was stolen from Hope Finance on Monday. 

 The project, an Arbitrum-based Tomb-fork, published a tweet accusing a team member of rugging the project, along with KYC information.

 FUCKING SCAMMER!!!! HE SCAMMED COMMUNITY FOR 2 MLN DOLLARS

 The official comms didn’t mince their words, even as they advised users on how to use the emergencyWithdraw function to attempt to salvage funds:

 Steps to withdraw your staked LP from the this fucking scam protocol

 While the official story may be of a dev gone rogue, the tx preparing the rug was approved by all three accounts on the team’s multisig. And faked KYC is not hard to come by.

 For users, the situation seems…

 Hopeless. 

 Credit: Certik 

 Funds were drained (~$800k in WETH and ~$1M in USDC ) from GenesisRewardPool contract at launch. 

 According to Certik’s analysis :

 In preparation for the @hope_fin exit scam, a fake router was deployed in txn 0xf188.

 The SwapHelper was then updated to use this fake router in txn 0xc9ee . This txn was approved by all 3 owners of Hope’s multisig 0x8ebd .

 In txn 0x1b47, 
```
 _swapExactTokenForTokens
```
 variable was set to wallet address, 0x957D .

 When 
```
GenesisRewardPool.openTrade()
```
 is called to borrow USDC, GenesisRewardPool transfers WETH to TradingHelper to convert to USDC.

 Instead of swapping, USDC was sent to 0x957D.

 As the 
```
_uSDC
```
 address was deliberately left empty, the receiving address ( 0x957D ) was passed to v2 and the 
```
swapExactTokensForTokens()
```
 transferred 477 WETH to 0x957D.

 Rug puller prep address: 0xdfcb9a03fbe9f616ee6827cd1b753238d53c6145 

 Rug puller receiving address ( ETH , ARBI ): 0x957d354d853a1ff03dda608f3577d24ea18fcece 

 Hope Finance Multisig: 0x8ebd0574d37d77bdda1a40cdf3289c9770309aa7 

 The USDC received was swapped to ETH, for a total of 1095 ETH, which was then bridged to Ethereum via Celer and finally deposited into Tornado Cash. 

 The project had two audits prior to launch, by Cognitos (the code passed despite auditors flagging two ‘major’ issues, neither of which related to the mechanism used to rug) and AuditRateTech (who appear to have deleted the audit report , although a KYC certificate still remains on their site).

 It’s impossible to know whether the doxxed individual accused by the team is truly to blame. 

 According to Streetview, the address given in the ID is a vacant lot . 

 And with many other possible explanations: bought KYC or even framed by someone else from the project with access to official comms.

 It’s possible that this case will end in whoever is responsible being brought to justice… 

 But don’t get your Hopes up. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
