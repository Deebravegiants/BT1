# [C] Ankr & Helio exploit: That’s the theoretical value of the 60 trillion aBNBc that was illegitimately minted from Ankr earlier today

## Summary
Severity: Critical
Target: Ankr & Helio
Loss: $24,000,000
Published: 12/02/2022
Source: https://rekt.news/ankr-helio-rekt
Type: rekt-postmortem

## Details
## Ankr & Helio - REKT

 Friday, December 2, 2022 Ankr - Helio - REKT 

 read this article also in : zh 

 18 quadrillion dollars. 
 That’s the theoretical value of the 60 trillion aBNBc that was illegitimately minted from Ankr earlier today.

 Unfortunately, that’s more than the GDP of the entire world, and the aBNBc liquidity couldn’t stretch that far, so the hacker only got away with $5M.

 Ankr’s official announcement pointed out that underlying staked assets are safe, and the thread goes on to promise users “a reissuance of aBNBc” via a snapshot.

 But the damage didn’t stop there… 

 Credit: BlockSec , Peckshield 

 aBNBc is a reward-bearing receipt token for BNB staked via the Ankr platform on BSC. 

 The exploit was due to a private key compromise of the Ankr deployer address on BSC, potentially the result of a phishing campaign .

 The compromised deployer account published a malicious version of the aBNBc token contract, which was then upgraded to replace the existing implementation. The upgraded version included a new function (0x3b3a5522) which allowed the attacker to bypass caller verification and mint tokens freely, directly to their own address.

 Exploiters address: 0xf3a465c9fa6663ff50794c698f600faa4b05c777 

 (Compromised) Ankr deployer address: 0x2ffc59d32a524611bb891cab759112a51f9e33c0 

 Example attack tx (minting aBNBc to exploiter’s wallet): 0xe367d05e… 

 Funding exploiter wallet from compromised deployer: 0xeb617798… 

 Despite the large amount of tokens minted, a lack of on-chain liquidity limited the exploiter’s profits to just $5M after draining PancakeSwap’s aBNB pools. Most of the proceeds were bridged to Ethereum , where the exploiter is in the process of laundering them through Tornado Cash.

 As the word got out about the publicly callable infinite mint, copycats joined in, many of whom can be seen amongst the top holders of the now worthless aBNBc. 

 Some did find a way to profit, however, with one account making 3x more than the initial exploiter, however the quick timing and recent funding of the address suggest that it could be the same actor.

 By buying large amounts of depegged aBNB from PancakeSwap, this address took the token to stablecoin project Helio Money .

 Before the oracle had updated to reflect the crashed price, the user borrowed 16M HAY against aBNBc collateral for a profit of $15.5M. Another user profited through the same method, earning approximately $3.5M.

 The attacks have caused HAY to depeg ($0.62 at the time of writing), but the project has assured its users that they will be compensated.

 Audits by both Peckshield and Beosin called out the danger that the privileged accounts posed to Ankr’s smart contracts, and were marked as “Confirmed” and “Acknowledged”, respectively. 

 However, Ankr did not take steps to fix these issues. 

 Now they have paid the price, and Helios has caught even more collateral damage.

 CZ tweeted the following summary: 

 ”Possible hacks on Ankr and Hay. Initial analysis is developer private key was hacked, and the hacker updated the smart contract to a more malicious one. Binance paused withdrawals a few hrs ago. Also froze about $3m that hackers move to our CEX.”

 Is CZ trying to become crypto’s new main character? 

 Someone should remind him that role never ends well… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
