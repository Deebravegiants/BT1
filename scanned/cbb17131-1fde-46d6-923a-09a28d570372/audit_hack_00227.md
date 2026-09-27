# [M] SafeDollar exploit: Your dollars are not safe and they never were

## Summary
Severity: Medium
Target: SafeDollar
Loss: $248,000
Published: 06/28/2021
Source: https://rekt.news/safedollar-rekt
Type: rekt-postmortem

## Details
## SafeDollar - REKT

 Monday, June 28, 2021 SafeDollar - Polygon - REKT 

 read this article also in : zh 

 Your dollars are not safe and they never were. 

 Users jump from chain to chain, but hackers follow hot on their heels. 

 Polygon has seen its user base grow in recent months, initially as an alternative to the congested Ethereum network, and then later to escape the Binance Smart Chain minefield , but it seems where there’s liquidity; there’s a loophole, and now everyones money is Polygone.

 Low-quality protocols get low-quality coverage , but you asked for more, so here it is. 

 Two hundred and forty eight thousand gone, from a protocol that was called “SafeDollar”. 

 If they need to tell you they’re safe, they usually are not. 

 Not only has SafeDollar seen its Polygon-based “stable” coin SDO drop to $0, but this isn’t even the first exploit the protocol has suffered this week. 

 ...we have met our 1st challenge but we will continue to work tirelessly to ensure the project stays on its course.

 Thank you for your understanding and support to SafeDollar.

 Writing a half-hearted post-mortem, congratulating yourself and thanking users for continuing to trust in your flawed project isn’t a great look.

 In fact, it looks more like an invitation.

 Less than two weeks ago we asked: 

 Are all algorithmic stablecoins bound to the same fate? 

 Only $250k taken this time, via an infinite mint exploit. 

 The exploit used a bug in SafeDollar’s reward mechanism to manipulate the accSdoPerShare value, eventually being able to claim vast quantities of SDO for each token deposited.

 An initial deposit into one of the protocol’s Safe Farms was made in preparation.

 The token that SafeDollar was incentivising, PLX , charges fees on transfers. These fees are supposedly borne by the user, but during withdrawal transactions these fees were deducted from the rewarder balance instead.

 A deposit/withdraw loop , allowed the hacker to gradually deplete the PLX balance of the pool over the course of 101 transactions, resulting in a massively inflated accSdoPerShare of 1,142,913,215,739,484,400 SDO being rewarded for each PLX deposited.

 With the rewards system now skewed, the attacker fired a final transaction. 

 Claiming the rewards on the initial deposit produced a total of 831,309,277,244,108,000 SDO , which was simultaneously sold, crashing the price of SDO straight to $0.00.

 Despite owning such an enormous quantity of the stablecoin, the attacker could only make off with the defunct coin’s exit liquidity of 202k USDC and 46k USDT.

 So, just $248k, not $248 million. 

 At position number 36 on the leaderboard , hopefully this will be the smallest hack we'll have to cover.

 Apparently CTRL C / CTRL V is just as popular when writing about DeFi protocols as it is when forking them. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
