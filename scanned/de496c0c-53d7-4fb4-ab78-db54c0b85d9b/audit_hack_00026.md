# [H] DODO exploit: DODO was hacked for $2 million using a fake token attack, but the motive remains unclear

## Summary
Severity: High
Target: DODO
Loss: $2,000,000
Published: 03/09/2021
Source: https://rekt.news/au-dodo-rekt
Type: rekt-postmortem

## Details
## DODO - REKT

 Tuesday, March 9, 2021 DODO - REKT 

 read this article also in : zh 

 Is it dead or has it just gone to bed? 
 DODO was hacked for $2 million using a fake token attack, but the motive remains unclear.

 One thing’s for sure, whether hat white or black, only $2 million? Must try harder.

 Twitter remains the fastest source of news for DeFi - even the DODO team relied on Luciano to tell them that their own $WCRES / $USDT pool had been drained using fake tokens.

 The following analysis is taken from the official DODO release, with thanks to @samczsun , @tzhen , PeckShield , and SlowMist .

 The exploits targeted several DODO V2 Crowdpools, namely the WSZO, WCRES, ETHA, and FUSI pools. 

 In total, approximately $3.8 million, of which $1.88 million is expected to be returned (see below for more information), was drained as a result of these exploits.

 The DODO V2 Crowdpooling smart contract has a bug that allows the init() function to be called multiple times. This means that an exploiter can perform an attack with the following steps:

 1. Exploiter creates a counterfeit token and initialize the smart contract with it by calling the init() function

 2. Exploiter calls the sync() function and sets the “reserve” variable, which represents the token balance, to 0

 3. Exploiter calls init() again to re-initialize - this time with a “real” token (i.e. tokens in DODO’s pools)

 4. Exploiter uses a flash loan to transfer all real tokens from the pools and bypass the flash loan check

 In summary, there are two individuals involved in this exploit. We will refer to them as Individual A and Individual B. 

 Individual B has all the hallmarks of a frontrunning bot, because:

- They constructed their contract address with a prefix of several 0s

- They use the CHI gastoken

- They set extremely high gas prices; in one instance they raise configured the transaction to use 93,148 gwei.

 In addition, Individual B’s exploits preceded Individual A’s successful exploits by roughly ten minutes.

 Individual A 

 Individual A has already contacted the DODO team through samczsun and offered to send back the funds removed from DODO pools. Here is a detailed account of Individual A’s actions:

 Individual A interacted with a centralized exchange.

 Individual A withdrew 0.46597 ETH from Binance:

 Individual A executed , in quick succession, 7 BUSD withdrawal transactions (see the link for one example), possibly involving the Binance Bridge:

 Individual A transfer their funds to another wallet address.

 Individual A transferred 67,416 BUSD to 0xa305fab8bda7e1638235b054889b3217441dd645 twice - ONE - TWO 

 Individual A transferred 59,245.324743 USDT to 0xa305fab8bda7e1638235b054889b3217441dd645 twice: ONE TWO 

 Individual A executed two exploits against DODO smart contracts.

 The first one was against the DODO-USDT test contract, and funds were transferred to 0xa305fab8bda7e1638235b054889b3217441dd645.

 The second one was against the WCRES-USDT contract, and funds were transferred to 0x56178a0d5f301baf6cf3e1cd53d9863437345bf9.

 The funds are now in the following two addresses: 

 0xa305fab8bda7e1638235b054889b3217441dd645 

 0x56178a0d5f301baf6cf3e1cd53d9863437345bf9 

 Individual B 

 Individual B is most likely a bot. (a robododo) 

 Suspected bot smart contract: 0x00000000e84f2bbdfb129ed6e495c7f879f3e634

 Trigger account address: 0x3554187576ec863af63eea81d25fbf6d3f3f13fc

 Individual B executed 3 exploits against DODO contracts: 

 ETHA-USDT: 0x0b062361e16a2ea0942cc1b4462b6584208c8c864609ff73aaa640aaa2d92428 

 WSZO-USDT: 0xff9b3b2cb09d149762fcffc56ef71362bec1ef6a7d68727155c2d68f395ac1e8 

 vETH-WETH, with 93,148 gwei: 0x561f7ccb27b9928df33fa97c2fb99ea3750593e908f9f0f8baf22ec7ca0c5c4a 

 The funds are currently in the following two addresses: 

 0x00000000e84f2bbdfb129ed6e495c7f879f3e634 

 0x3554187576ec863af63eea81d25fbf6d3f3f13fc 

 The DODO team are currently trying to contact the owners of the above addresses.

 A relatively small sum of $2 million taken by an anonymous actor. 

 It’s likely that the colour of the hat changes according to the sums of money that are available.

 Small sum = white hat for clout - Big sum = take it and add it to the other millions.

 We can only imagine the personal treasuries that these individuals are accumulating. There is so much opportunity out there, and not just for those who choose to learn to code.

 It’s noteworthy that even the teams themselves rely on Twitter for updates on their own protocols. This serves as a reminder that we truly are still in the early stages of this industry.

 The opportunity to make your name is clear - what you do with the power remains up to you.

 Image credits - harrikallio.com & @BxST23 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
