# [C] Eminence - Rekt in prod exploit: Andre Cronje’s unreleased project Eminence has been hacked for $15 million

## Summary
Severity: Critical
Target: Eminence - Rekt in prod
Loss: $15,000,000
Published: 09/28/2020
Source: https://rekt.news/eminence-rekt-in-prod
Type: rekt-postmortem

## Details
## Eminence - Rekt in prod

 Tuesday, September 29, 2020 yfi - defi - hack - Eminence - Cronje 

 read this article also in : zh 

Andre Cronje’s unreleased project Eminence has been hacked for $15 million. 
 The crypto community went into yet another frenzy last night, as Andre Cronje's unreleased project became the focus of hundreds of users, who quickly bought $15 million of the mysterious $EMN token.

 After some unexplained promotional tweets, users were keenly watching Cronje's account for any clues as to what was coming. As soon as the new contracts were deployed from the yEarn finance address, the game was on.

 Hundreds of users joined in the crowd-sourced investigation project to try and understand what was going on, and how to profit.

 Users linked the graphics from the eminence.finance Twitter account to an unfinished MMORG called Eminence, Xander's Tales.

 pic.twitter.com/tV9LSzPXlV > — eminence.finance (@eminencefi) September 28, 2020 

 You're hearing it here first, certified alpha leak, I smell the rebirth of an old card game with an NFT/DEFI twist... $ENM 

 Do some digging on "Eminence: Xander's Tales" and you'll find that @AndreCronjeTech even follows the lead artist for the project... 👀

 More soon, follow me
— Kiyo (@IslandKiyo) September 28, 2020 

 The contracts that had been deployed included the EMN token, which could be exchanged for other tokens such as eYFI, eAAVE, or eSNX. These tokens, plus the surprise launch, matched perfectly one of Andre's previous tweets about the upcoming yEarn finance project.

 The new yearn system is probably the most complex to date. It incorporates @synthetix_io @AaveAave @chainlink @iearnfinance and will be running on L1/L2

 Trying to decide if we should do whitepaper-esque writeups to explain before launch, or just launch and surprise everyone?
— Andre Cronje (@AndreCronjeTech) September 23, 2020 

 Cronje's reputation as a leading DeFi builder, combined with his promotion of the Eminence Twitter account, caused a full on frenzy, and $15 million flowed into the unexplained contract to be exchanged for EMN or one of the eTokens.

 🚨 yearn system confirmed.

 LAUNCHED AND SURPRISED EVERYONE.

 JFC the madman is doing it again.

 LONG $YFI pic.twitter.com/XO5ZkJxDCq > — BlueKirby.eth // YFI 🔥 (@bluekirbyfi) September 28, 2020 

 Despite the EMN token originating from a relatively flat bonding curve, many users were purchasing the tokens "second hand" from Uniswap, which led to a few hours of very profitable arbitrage for those who were comfortable interacting directly with the contract.
 
 At around 04:00 UTC, the $15 million contained in the contract was suddenly drained.

 @fifikobayashi wrote a short summary of how the attack took place.

- Use flash loan to mint EMN

- Manipulate EMN price downwards by burning EMN for eTokens

- EMN is based on a bonding curve, so when supply goes down, price goes down.

- Short EMN by burning the other half of the flashed EMN back into DAI, which was then inflated in comparison due to the curve-induced drop in EMN value.

 Although hacks are certainly not unusual in crypto, what happened next certainly is.

 11 minutes after removing $15 million in DAI, the attacker returned $8 million to the Yearn: Deployer contract 01:31:04 AM +UTC.

 Ethereum Transaction Hash (Txhash) Details | Etherscan

 Ethereum (ETH) detailed transaction info for txhash 0x7bc97357364222207f1f011b22ad98ba78fcd3c25d3398346caa3928cdf4a4dd. The transaction status, block confirmation, gas fee, Ether (ETH), and token transfer are shown. 

 etherscan.ioEthereum (ETH) Blockchain Explorer 
 
]( https://etherscan.io/tx/0x7bc97357364222207f1f011b22ad98ba78fcd3c25d3398346caa3928cdf4a4dd )
Theories are running wild about who was behind the hack, and why they would return any money, with some pointing the finger at the creators of Yearn Finance, and claiming it was an inside job. 
 
 So.. was it @bantg who ran multiple bots, inflated the SHIT out of #EMN (and more) to arb DAI and eventually dumped for the growing liquidity? https://t.co/vKOKs7IlxF https://t.co/rbb8H6c78H https://t.co/V7ocyAQg0J @ChainLinkGod @AndreCronjeTech pic.twitter.com/9Dle86Yffy > — Spicetoshi (@Spicetoshi) September 29, 2020 

Ultimately, those who deposited funds into the unaudited contracts are responsible for the loss of their money, however many have branded Cronje's promotion of the unfinished contract to be irresponsible, as the resulting FOMO could have easily been predicted. 
 One thing is for certain, a lot of people lost money last night.

 Can we pour one out for our 🐋 whale brother here that spent $130,548 for $EMN 1.5 hours ago and just sold it recently for $368. https://t.co/5iVIHS93Pv https://t.co/GBUMc62Eqs pic.twitter.com/jIa7WVwP6s > — fomosaurus 🦖 (@fomosaurus) September 29, 2020 

 FOLLOW UP POST: MANS SPENDS 100k TO MAKE $348 - MAD RESPECT TO THE GALAXY BRAIN DEGEN KING WHO RISKED IT ALL FOR AN ETH $EMN pic.twitter.com/IZnBSTMfqs 
— end i i i (@end0xiii) September 29, 2020 

 #rekt

 i bought just over $100,000 $EMN before the hack/exploit. i think my life is over
— zerosum (@zerosum666) September 29, 2020 

 Cronje claims to have received multiple threats regarding the lost funds, and has asked Yearn Treasury to assist with distributing the returned $8 million.

 Despite this major setback, Andre continues to build, and released this tweet earlier today.

 I am still building @eminencefi . I love the metaverse and metaconomy.

 I am also going to continue deploying test contracts. I have over ~100 deployed contracts, of which probably >half have vulnerabilities.

 Please wait for official announcements.
— Andre Cronje (@AndreCronjeTech) September 29, 2020 

 Yearn developers Banteg and Klim K have also been working hard to help those affected, and have created a snapshot of EMN and the eTokens in order to try and refund those who lost money.

 Users can check their eligibility here (divide by 1e18)

 rektHQ was not involved in the creation of this list, and no details are final.

 Since we have received 8M DAI, we are working towards distributing them to the people who got rekt. I have finished the first version of the snapshot which uses bonding curve rates of EMN, eCRV, eLINK, eAAVE, eYFI, eSNX at block 10954410. It includes 3656 addresses. pic.twitter.com/dT3WryyGrD > — banteg (@bantg) September 29, 2020 

 Last night's proceedings were the culmination of several different events, attitudes, and concepts that have arisen over recent months.

 Those who have FOMO'd into unaudited contracts have been rewarded well in the past, and although many on Twitter are keen to promote this style of "Chad" behaviour, perhaps it's time to rethink this style of surprise launch.

 The previously unblemished reputation of the YFI developer has taken a hit, and we are now at what feels like a turning point in DeFi, where hopefully both developers and users can learn from this event.

 Until then, we look forward to the real release of Eminence: Xander's Tales.

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
