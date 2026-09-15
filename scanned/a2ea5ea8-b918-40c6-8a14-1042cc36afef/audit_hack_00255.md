# [H] SushiSwap exploit: Over $3.3M was stolen from SushiSwap users over the weekend via a new routing contract

## Summary
Severity: High
Target: SushiSwap
Loss: $3,300,000
Published: 04/09/2023
Source: https://rekt.news/sushi-yoink-rekt
Type: rekt-postmortem

## Details
## SushiSwap - REKT

 Monday, April 10, 2023 SushiSwap - REKT 

 read this article also in : zh 

 Yoink. 

 Over $3.3M was stolen from SushiSwap users over the weekend via a new routing contract. 

 All users who had approved Sushi’s 4 day old RouteProcessor2 contract at the time of the incident, were at risk, across 14 chains .

 Sushi Head Chef, Jared Grey, acknowledged the bug, urging users to revoke approvals. He later stated that the protocol is now safe to use, and the exploited contract has been removed, as well as promising a full post-mortem on events. 

 Amongst the chaos, DeFi’s favourite villain got rekt for 1800 ETH, and there was plenty of whitehacking activity . 

 One user claimed to have targeted 0xSifu as a whitehat, though the attempt appeared to have been botched , with only 100 ETH eventually returned . BlockSec also got involved, adding to their impressive list of recent whitehacks .

 Luckily, the days-old contract had relatively few approvers, and this didn’t turn out to be the AMM-ageddon it could have been.

 But this is a bad look for an already-embattled protocol, nonetheless. 

 How many more scandals can Sushi take? 

 Credit: Inspex , 0xfoobar , ernestognw 

 The new contract contained the function, processRoute, which is insufficiently protected against accepting arbitrary data.

 The attacker was able to create a fake Univ3 pool, and insert their own contract address in place of a genuine liquidity pool. During the uniswapV3SwapCallback function, the contract is then able to drain (or 'yoink' ) tokens from any address which had approved it.

 As 0xfoobar explained :

 SushiSwap router exploit comes from a bad callback. Although the line 328 comment is correct, line 340 does not check the pool deployer. So you can impersonate a V3Pool, do a no-op swap, call safeTransferFrom on an arbitrary ERC20 and arbitrary 
```
from
```
 address on line 347

 A more detailed breakdown was provided by ernestognw.eth.

 Example attack tx: 0xea3480f1… 

 RouteProcessor2 contract on ETH: 0x044b75f554b886A065b9567891e45c79542d7357 

 See this list for addresses to revoke across multiple chains. 

 Rather than an existential threat to SushiSwap, this incident is more of an embarrassment than anything. 

 The damage wasn’t enourmous, nor particularly widespread . Users were either drained or revoked quickly, and whitehat efforts certainly helped to soften the PR blow.

 Ever since its launch, though, Sushi has been surrounded by drama. 

 2020’s DeFi summer saw Sushi come onto the scene in dramatic fashion, quickly establishing itself as one of DeFi’s darlings, alongside Uniswap, Curve, Aave and Compound.

 However, a period of stagnation during the 2021 bull run ended in infighting . Then, in October, the new head chef, Jared Grey’s, murky past in a variety of struggling projects drew suspicion. 

 Sushi seems to be a good case study for DAOs working, until they don’t.

 A small team of highly-motivated devs can disrupt the DEX landscape in just weeks. But once the excitement wanes, a bloated team can get too comfortable with inactivity and apathy (or simply farming a project’s treasury).

 Grey receiving an SEC subpoena, criticism of a paltry bug bounty programme, and large operating expenses (including 500k for Grey himself)...

 It appears the drama is far from over for Sushi. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
