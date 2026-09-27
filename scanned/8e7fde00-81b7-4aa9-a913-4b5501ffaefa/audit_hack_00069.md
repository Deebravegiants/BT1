# [H] Cover exploit: Infinite mint but it’s no Willy Wonka - this is a Hollywood classic insurance themed noir

## Summary
Severity: High
Target: Cover
Loss: $9,400,000
Published: 12/29/2020
Source: https://rekt.news/cover-rekt
Type: rekt-postmortem

## Details
## Cover - REKT

 Tuesday, December 29, 2020 cover - Rekt 

 read this article also in : zh 

 Next time, take care of your own shit. 
 Infinite mint but it’s no Willy Wonka - this is a Hollywood classic insurance themed noir.

 The black and white outcomes of insurance policies lend themselves well to Hollywood storylines.

 In Double Indemnity (1944), insurance is the motivating force for both good and evil. 

 The film takes its name from a life insurance clause that offers double payouts if the death of the policyholder is accidental.

 This results in a twisting plot as an insurance salesman is roped into a murderous scheme by his lover, who wants him to murder her husband and frame it as an accident in order to profit from the payout.

 Never take anything at face value. DeFi plot lines are rarely straightforward. Anonymity and composability are the perfect breeding ground for conspiracy; there are multiple ways one can profit from a single incident, meaning smart players don’t always take the most obvious reward.

 $9.4m taken, $3.2m recovered and $6.2m lost. 

 COVER (formerly known as SAFE) fell ~ 90% when an infinite mint loophole was uncovered and exploited, causing the total supply of tokens to increase by 48 quadrillion percent, from 84,477 to 40,796,131,214,802,600,000.

 Six different addresses minted COVER via this loophole before it was closed. Some kept the money, others did not. 

 Of the six addresses to use the loophole, the previously unknown Grap Finance gained the most attention, as they took the opportunity to present themselves as a “White hat” by selling minted COVER for ETH and returning it with a sassy message.

 Code is law, but loopholes remain - we can rely on attackers to take advantage, but we know things are rarely as simple as they seem.

 Who had cover on their $COVER? We went undercover to find out.
 
 Rekt OPSEC 

 The original attack had four steps and one attacker, but the story became more complicated once the loophole was made public , and other wallets replicated the process.

 The following timelines are taken from the official Cover Post-Mortem , for a more detailed analysis, please see the step by step from @vasa_dev .

 Timeline for Exploiter 1 

 Dec-28–2020 04:09:27 AM +UTC

- A new Balancer pool was added to the Blacksmith contract from the team’s multisig via a transaction for the new coverage expirations.

 Dec-28–2020 08:08:12 AM +UTC

- An attacker executes the first deposit to the contract , depositing 1,326,880 BPT tokens

 Dec-28–2020 at 08:11:16 AM +UTC

- The same attacker then called withdraw(), exploiting the contract for ~703.64 $COVER and withdrawing 1,326,878.99 BPT

 Dec-28–2020 08:47:15 AM +UTC

- The first sell of the exploited $COVER tokens can be found here . During this time there were multiple accounts abusing the exploit, and selling their $COVER on market.

 Dec-28–2020 09:18:28 AM +UTC

- The attacker continues minting while the attack vector is still present.

 In total, Exploiter 1 stole around $4.4 million of user funds and transferred it to this address . 

 It seems the loophole was discovered accidentally at first, as exploiter 1 had poor OPSEC, a normal wallet funded by an exchange with KYC, trading for 3 years. Some claim to know the identity of this exploiter, and suggest that they return the funds.

 In a classic DeFi plot twist, the original attacker attracted little attention compared to Grap Finance, who seized the opportunity to play the role of “White Hat”. 

 Timeline for Grap Finance 

 Dec-28–2020 11:54:47 AM +UTC

- Grap Finance: Deployer (Externally owned account) deposited 15,255.552810089260015362 BPT (DAI/Basis pool) into the Blacksmith farming contract.

 Dec-28–2020 11:58:04 AM +UTC

- Grap Finance: Deployer withdraws their 15,255.552810089260015361 BPT (DAI/Basis pool), leaving just 1 wei in their balance in the Blacksmith farming contract.

 Dec-28–2020 11:58:56 AM +UTC

- Another user withdraws most of his full balance (1,007.599009946121991627 BPT) from the Blacksmith. Now Grap Finance alone has all liquidity for the DAI/Basis pool on the shield mining Blacksmith contract, exactly 1 wei.

 Dec-28–2020 12:00:21 PM +UTC

- Grap Finance: Deployer deposited back 15,255.552810089260015361 BPT (DAI/Basis pool) on the Blacksmith farming contract..

 Dec-28–2020 12:02:04 PM +UTC

- Grap Finance: Deployer claimed the rewards , and because of only 1 wei of balance combined with the storage/memory issue this led to the minting of 40,796,131,214,802,500,000.212114436030863813 $COVER.

 Dec-28–2020 12:29:03 PM +UTC

- Grap Finance: Deployer starts to sell as many tokens as possible through 1inch.exchange in multiple transactions.

 Dec-28–2020 12:59:27 PM +UTC

- Grap Finance: Deployer burns minted tokens 

 Dec-28–2020 at 01:41:01 PM +UTC

- Grap Finance: Deployer sends the 4351 ( 1 + 4350 ) ETH they have extracted by selling $COVER to the deployer account , which accounts for 34% of the total exploit damage ($9.4 million)

 Coverage from Cover 

 It took six hours for Cover Protocol to publicly acknowledge the attack. 

 The team is still investigating the current incident. The exploit is no longer possible. 

 Please do NOT buy $COVER tokens, and remove your liquidity from the COVER/ETH pool on sushiswap. 

 CLAIM/NOCLAIM balancer pools are unaffected 

 Eight hours after the attack, Cover protocol announced their plan to refund affected users. 

 Hello everyone, we are exploring providing a NEW $COVER token through a snapshot before the minting exploit was abused. The 4350 ETH that has been returned by the attacker will also be handled through a snapshot to the LP token holders.We are still investigating. Do NOT buy COVER 

 “What is dead may never die” appears never more true than in DeFi . A fourth iteration of the Cover Protocol token will be issued to refund the affected users.

 SAFE - SAFE2 - COVER - $RECOVER? 

 Persistence is admirable up to a certain extent, but when is enough enough? 

 Some readers will remember the full history of Cover Protocol, who rebranded from SAFE after both @azeemfi and @chefcoverage made poor decisions. They then launched SAFE2, which was migrated to the COVER which we know today.

 Is the community is willing to give them a FOURTH opportunity?

 Grap Finance is a fork of YAM - who having failed to ship anything noteworthy during DeFi summer, jumped at the opportunity to gain attention by presenting themselves as a White Hat, which gained them thousands of followers in just one day.

 What they will do with this new found following remains to be seen.

 Grap Finance ’s unusual activity puts them within the top five balance changes for COVER within the last 7 days.

 They say there’s no such thing as bad publicity, and this seems to be confirmed by the next chart - unique addresses for COVER increased on the day of the attack by 1,778, as opportunist traders tried to catch a falling knife.
 
Here we see Binance shown in green, a huge increase in COVER deposits as the community tried to jump ship before they eventually paused trading for the token.
 
Responsible behaviour may not offer much reward, but wages of sin are always paid in full. 
 Some say this was an insider job gone wrong.

 Perhaps the attackers got doxxed, couldn’t keep the funds, so sent them back and profited from promo instead.
 
 We don’t claim that these rumours are based in fact, but it’s easy to see how such ideas arise when the day's events lead to announcements such as this .

 Pure coincidence is out of the question , this is foul play or desperation. MXC must have fallen on hard times if they’re listing tokens based on gossip.

 Crypto Twitter has proven that their risk appetite remains strong by pumping the price of their “rescuers” token by several thousand percent, increasing its 24hr trading volume from $236 to $5,458,084 at the time of writing.

 Emiliano Bonassi provided the following quote: 

 Setting a side the technical issue, this event showed again how this ecosystem is cohesive and supportive. 

 We are antifragile. 

 I am pretty sure that after this event not only a new Cover will emerge but more importantly a collective to guarantee safety and prompt reaction in the ecosystem - maybe The WhiteHack Group 

 Blood is a big expense. The DeFi insurance market is in a sorry state. 

 First NXM and now Cover. It doesn’t matter if the protocol is unaffected, if we have to write an article about you, then the user's confidence in your project has already gone.

 DeFi insurance must be fully comprehensive. Acts of god don’t happen here.

 Insecure protocols pay high premiums, while others work hard to build their no claims bonus.

 COVER went down 40x in 4 hours while $GRAP went up 40x.

 “No gains” say Grap team from behind their screen , a tall tale that tells half the truth.

 Black hats painted white don’t last under a shower of allegations. 

 The investigation continues...

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
