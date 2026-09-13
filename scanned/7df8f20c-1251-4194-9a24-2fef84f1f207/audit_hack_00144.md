# [H] Kokomo Finance exploit: This time, Kokomo Finance took off with approximately $4M, deleting their website, Twitter , GitHub and Medium in the process

## Summary
Severity: High
Target: Kokomo Finance
Loss: $4,000,000
Published: 03/26/2023
Source: https://rekt.news/kokomo-finance-rekt
Type: rekt-postmortem

## Details
## Kokomo Finance - REKT

 Monday, March 27, 2023 Kokomo Finance - Optimism - Rugpull - REKT 

 read this article also in : zh 

 Another week, another rug. 

 This time, Kokomo Finance took off with approximately $4M, deleting their website, Twitter , GitHub and Medium in the process. 

 The lending protocol had launched on Optimism less than a week ago, and its token, KOKO , less than 36 hours before the rug.

 Wrapped Bitcoin deposits were rugged via changes made by the project’s deployer address. Almost $2M of tokens still remain in the project’s pools on Optimism. 

 But with the contracts paused and users unable to withdraw funds, the question remains…

 …will they be back for the rest? 

 Credit: Certik , Beosin 

 Certik explained how the rug went down:

 1/ The deployer of KOKO Token, address 0x41BE , deployed attack contract cBTC. Then set the reward speed, paused the borrow and set the implementation contract into a malicious one .

 2/ Address 0x5a2d … approved the cBTC contract to spend the 7010 sonne WBTC.

 3/ Since the implementation contract has been upgraded to the malicious cBTC contract, the attacker called 0x804edaad method to transfer sonne WBTC to address 0x5C8d .

 4/ Finally, the address 0x5C8d.. swapped 7010 sonne WBTC to 141 WBTC (~4M) for profit.

 The rugged funds are currently in the following addresses: 

 0x8C0eCD7BACCed114729F8269B459E0A4D5e95C3b 50 BTCB ($1.4M)

 0xB74C5e41E748BaBC32ce33813549E2503CDaB762 40 BTCB ($1.1M)

 0xC2AE8D3b0fb159cCD331a01A8C3632B95dB23CF5 32 BTCB ($0.9M)

 0x88340ff2292506D0D93934CbBFEA5ED1804CDa0d 20 WBTC ($0.6M)

 The project’s audit , conducted by 0xGuard, covered just the token contract, rather than the protocol at large.

 Aside from Wintermute’s Gnosis Safe blunder last year, this is the largest incident we’ve covered on Optimism, so far. 

 With last week’s ARB airdrop taking all the L2 mindshare, and now this bad news for Optimism…

 Are we seeing a changing of the tides amongst Ethereum’s most popular scaling solutions? 

 Or now that airdrops are out of the way, will users simply rotate to the next best chance to ‘earn’ some free money?

 Whatever the future holds for Optimism, one thing’s for certain: 

 Kokomo has flatlined. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
