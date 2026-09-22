# [H] Money for nothing? exploit: $1.3M was lost on Tuesday when a Uniswap V3 whale LP made a costly fat-finger error

## Summary
Severity: High
Target: Money for nothing?
Loss: $1,300,000
Published: 12/26/2023
Source: https://rekt.news/moneyfornothing
Type: rekt-postmortem

## Details
## Money for nothing?

 Thursday, December 28, 2023 MEV - Uniswap - REKT 

 read this article also in : 

 The cost of doing business? 

 98%. 

 $1.3M was lost on Tuesday when a Uniswap V3 whale LP made a costly fat-finger error. 

 The victim, aavebank.eth ( no apparent relation to the lending protocol ), is no stranger to bad luck.

 However, instead of picking up the back-run profits for themself, an MEV bot paid 98% of the take as a bribe to the block’s lucky solo validator . 

 In the dark forest of MEV extraction, enormous sums are routinely weaponised, often to shave off mere crumbs from the amounts involved.

 Amongst such cutthroat competition between ever-evolving bots, the block reward lottery's top prizes are growing. And with the increasing centralisation caused by liquid staking providers, the house ( almost ) always wins.

 Should validators be rewarded quite so generously for sitting on their stakes while searchers seek out the opportunities only to pay hefty bribes?

 Or should predatory MEV bots be grateful for any scraps they can get?

 Do either of them deserve the spoils? 

 Credit: Peckshield 

 Despite its deceptive name, we should all be well acquainted with the risks of ‘impermanent loss’ by now, Uni V3 LPs more than most.

 But far greater risks come from within. 

 Illiquid pools and fat fingers make for a dangerous combination on DeFi’s biggest DEX, where MEV bots are waiting to scoop up the spoils of even the slightest mistake.

 aavebank.eth added 2M USDT of liquidity at a very out-of-range pricepoint to the UNI-USDT pair, before burning the LP position to withdraw just 99k UNI (worth $730k) just two minutes later. 

 In the meantime, MEV bot 0xfde0d1 had eaten the excess USDT worth almost $1.3M from the costly, albeit juicy, error.

 Out-of-range LP positions on V3 can be used to set limit orders. One user pointed out :

 aavebank.eth has added followed a similar pattern in the past where they add $2 million USDT out of range essentially setting a limit order to buy UNI in the future. However, this time they fucked up the range and essentially offered to buy $730k UNI for $2m USDT.

 While the victim LP holds the ENS aavebank.eth, the address doesn’t appear to have a connection to the Aave protocol or team. 

 But that doesn’t mean experienced DeFi teams aren’t making similar blunders . 

 In ensuring they would be the one to grab the spoils, the bot gave up the majority of the 578 ETH profit in a 566 ETH ($1.25M) bribe paid to the validator, keeping just 2% for their trouble. 

 While previously a niche and lucrative racket, MEV has increasingly become a race to the bottom . 

 It may be entertaining to watch the occasional examples of on-chain karma as these blockchain predators feast upon one another, but MEV bots can also be responsible for returning frontrunned hack attempts ( in this case, the bot responsible is tagged on Etherscan as having thwarted two hacks to date ).

 Whenever someone loses out, be it to a sandwich attack or fat-finger mishap, a blockchain predator will snap up their losses.

 But pickings are getting slimmer as the arena becomes more crowded. 

 Bots willing to take the lowest profit margin are able to take it all, while validators sit back and feast on gradually more generous portions. 

 When excess value comes directly from malicious behaviour , should the recipients feel obliged to return the ill-gotten gains ?

 Lido certainly doesn’t think so . 

 So will these bumper rewards simply serve to drive up rates on liquid-staking behemoths, leading to further concentration of mainnet’s validators? 

 Or might it encourage more users to solo stake, hoping to hit the bribe jackpot themselves? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
