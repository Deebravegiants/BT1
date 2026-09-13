# [H] ChainSwap exploit: A new type of attack is growing in popularity

## Summary
Severity: High
Target: ChainSwap
Loss: $4,400,000
Published: 07/11/2021
Source: https://rekt.news/chainswap-rekt
Type: rekt-postmortem

## Details
## ChainSwap - REKT

 Tuesday, July 13, 2021 ChainSwap - REKT 

 read this article also in : zh 

 A new type of attack is growing in popularity. 
 As the demand for DeFi increases across chains, the bridges that join them turn into targets themselves.

 ChainSwap rekt, and not for the first time. This is the second incident this month in which the Alameda-backed “cross-chain hub for all smart chains” has lost users' funds.

 First $800,000, now $4.4 million. 

 The ChainSwap team needs to increase security $ASAP. 

 Attacker address: 0xEda5066780dE29D00dfb54581A707ef6F52D8113 

 On the Ethereum network, each token to be bridged has its own proxy Factory contract. The attacker was able to exploit the contract, minting tokens directly into different addresses, before reaccumulating them into the wallet from which the transactions were initially sent.

 1. Call receive function to the Factory (minting) contract

 2. Dodge the sloppy auth check system using a new address as signature each tx

 3. Pay 0.005 ETH chargeFee 

 4. Set to parameter to the desired address, which receives the minted volume

 5. Repeat x times

 Credit: @cmichelio 

 Over on BSC, the exploit targeted a total of 20 tokens, according to ChainSwap’s post-mortem. 

 Taking the example of the NFT platform WilderWorld, this is one of 40 repeated transactions, each of which minted 500,000 $WILD tokens each time.

 These 20M WILD were then sold for ~650 WBNB, or just over $200,000 USD via PancakeSwap, effectively depleting the WILD/WBNB pool in the process.

 By the time the hacker was finished, their wallet had filled with a variety of tokens, with a total value of approximately $4.4M. 

 The evidence is present in the attacker's Ethereum wallet taking the form of a long series of 0.005 ETH transactions, each evidence of freshly minted tokens via the Chainswap bridge. 

 The last few transactions show the attacker cashing out some of the ETH that had been bridged from BSC, via 1inch - a series of 5 transactions totalling 456 ETH, or approximately $935,000 at the time of writing.

 If the bridge isn’t the target, then it’s part of the escape route for this new style of cross chain attack. 

 BSC, Solana, Polygon, are all seeing increased activity, and as the liquidity grows, the loopholes will show. This won’t be the last time we see this type of hack.

 We didn’t cover the initial exploit. With so many to choose from, we need to set some standards. If it’s under a million dollars lost then there has to be something that piques our interest.

 However, when we looked back at the first post-mortem, we found this email that we thought might interest you. 

 A strange correspondence that the ChainSwap team claims to be from their attacker. 

 Or did the “great people” at ChainSwap just send it to themselves? Everyone is free to speculate...

 We are left wondering... why would the hacker fund his wallet with money from Tornado and then change his bounty into a centralised stablecoin such as USDT? 

 This leaves him vulnerable to having his funds frozen by Tether, and he hasn't tried to cover his tracks. 

 Is this a ChainSwap insider trying to prove a point, or has the email sender with “fake KYC accounts” returned for more? 

 Why has this money still not been laundered? 

 ChainSwap have arranged a full compensation plan for those affected by the attack, but the reputation of their platform can’t be refunded.

 A chain is only as strong as its weakest link… Who will break next? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
