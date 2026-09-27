# [H] Revest Finance exploit: A financial NFT platform which “offers instant liquidity for locked assets”, fell victim to a reentrancy attack

## Summary
Severity: High
Target: Revest Finance
Loss: $2,010,000
Published: 03/27/2022
Source: https://rekt.news/revest-finance-rekt
Type: rekt-postmortem

## Details
## Revest Finance - REKT

 Monday, March 28, 2022 Revest Finance - REKT 

 read this article also in : zh 

 ~$2M taken from Revest Finance. 

 A financial NFT platform which “offers instant liquidity for locked assets”, fell victim to a reentrancy attack.

 A fast reaction from the Revest team prevented them from losing more funds, however, they still take a place on the leaderboard (#67) .

 How did it happen? 

 The Revest team were informed of the “exploit at 2:24 UTC from the BLOCKS DAO development team ”. 

 In addition to BLOCKS DAO , substantial losses were also suffered by EcoFi and RENA Finance. 

 By halting transfers of RVST tokens, the team thwarted the attacker’s attempt (70 secs later) to drain the RVST-ETH pool on Uniswap, avoiding a further $1.15M in losses.

 The attacker’s dump of the stolen tokens had a large impact on the price of BLOCKS (initially down >95%, currently down ~80%) and ECO (down ~98%), however the RENA tokens remain untouched in the attackers address. 

 Credit: @BlockSecTeam 

 The root-cause of the attack was due to a reentrancy vulnerability in the ERC1155 minting contract ( example tx: RENA ) 

 The function mintAddressLock , used to create new Smart Vaults, contains two critical parameters: quantities and depositAmount .

 Revest Vault invokes the mint function of FNFTHandler, to mint quantities of ERC1155(s) with the next fnftId to the recipient(s) which can later be burned in order to claim the position’s proportion of locked tokens. fnftId increments by 1 each time the function is executed.

 Extra funds can be deposited to the FNFT using the depositAdditionalToFNFT function, deposits must be in the same proportion as defined by quantities , specifically: quantity==FNFTHandler.getSupply(fnftId) .

 If the above statement is not fulfilled, the user's share will be extracted from the position and transferred to a new FNFT with a balance defined by the existing position's depositAmount plus the newly deposited amount.

 Given that the existing position’s depositAmount is used, but fnftId (informed via fnftsCreated ) is not updated until the end of the minting routine, re-entrancy at this point allows for additional funds to be added to an existing position.

 Step by Step: 

 1: Attacker uses the mintAddressLock function to open a new position with fnftId=1027 , depositAmount=0 , quantities=[2] , asset=Rena , and recipients=[malicious contract] . Since the depositAmount X quantities[0] = 0 X 2 = 0 , the attacker transfers zero Rena.

 2: Attacker uses the mintAddressLock function again to open a new position with fnftId=1028 , depositAmount=0 , quantities=360,000 , asset=Rena , and recipients=[malicious contract] . Again, the attacker transfers zero Rena and receives 360,000 tokens (with fnftId=1028 ). Note that these 1028-tokens have no value now.

 3: At the end of Step 2, during the mint function of FNFTHandler , the attacker re-enters the Revest contract via the onERC1155Received interface. The depositAdditionalToFNFT function is used with amount = 1e18 , quantities=1 , fnftId=1027 , which would normally open the fnftId=1029 (new) position. However, due to the delay in updating fnftId , position 1028 is overwritten with the above data, ascribing value to the 1028 tokens owned by the attacker.

 4: The attacker uses the withdrawFNFT function to withdraw the 360,000 X 1e18 Rena tokens after having deposited only 1 quantity X 1e18 Rena tokens in Step 3.

 Token losses (approx $2M total) according to the official post-mortem report :

 350k RENA (~$125k, still in attacker’s address ) 

 715M BLOCKS (~$1.7M) 

 7.7M ECO (~$100k) 

 Smaller amounts ($10-$12K) of ConstitutionDAO and LUKSO were also stolen. 

 After swapping the majority of the stolen tokens for ETH, the attacker deposited the funds into Tornado Cash.

 A security breach is never a good look for a DeFi protocol, especially when its product is a secure locker to be trusted with other project’s tokens. 

 “One audit is never enough” says Revest, as they found that the vulnerability was not picked up in the project’s audit (solidity.finance).

 The team’s quick response and thorough post-mortem are promising signs, and although Revest have stated that “ we do not possess the funds needed for meaningful financial recompense ”, the postmortem report stresses the desire to make things right in the future.

 At the moment, it’s not clear how that will happen. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
