# [H] RIP MEV BOT exploit: The notorious MEV bot known as 0xbad has fallen on hard times, just like the rest of us

## Summary
Severity: High
Target: RIP MEV BOT
Loss: $1,500,000
Published: 09/27/2022
Source: https://rekt.news/ripmevbot
Type: rekt-postmortem

## Details
## RIP MEV BOT

 Wednesday, September 28, 2022 MEV - REKT 

 read this article also in : zh 

 Zero pity. 
 The notorious MEV bot known as 0xbad has fallen on hard times, just like the rest of us.

 After 75 days of exploiting value from unexpecting users, this mempool menace backfired on its owner, creating a beautiful display of on-chain karma.

 After one unfortunate user tried to swap $1.85M of Compound cUSDC for USDC on Uniswap v2, a lack of liquidity meant they only received $500 in USDC. 0xbad was quick to profit from the swap, backrunning the trade with an elaborate arb involving many different DeFi dApps.

 $1.02M profit.

 Nice. 

 However… 

 0xbad got put down… tremendously . 

 An anonymous attacker noticed a flaw in the bots arbitrage contract code, and stole not only the recently acquired 800 ETH, but the entire 1,101 ETH in 0xbad’s wallet.

 Attacker’s address: 0xb9f78307ded12112c1f09c16009e03ef4ef16612 

 0xbad: 0xbadc0defafcf6d4239bdf0b66da4d7bd36fcf05a 

 @bertcmiller of Flashbots broke it down:

 0xbad did not properly protect the function that they used to execute the dYdX flashloans.

 Note "callFunction," which is the function called by the dYdX router as a part of flashloan execution

 When you get a flashloan the protocol you're borrowing from will call a standardized function on your contract. 

 In this case dYdX called "callFunction" on 0xbad.

 Unfortunately for 0xbad, their code allowed for arbitrary execution.

 The attacker used this to get 0xbad to approve all of their WETH for spender on their contract.

 The attacker then simply transferred the WETH out to their address.

 Down 0xbad 

 To add further drama to the drama, 0xbad decided to try and threaten their attacker with a message sent via transaction input data. 

 Congratulations on this, we got careless and you sure managed to get us good, that was not easy to see. We would like this cooperate with you on resolving this matter. Return the funds to @x19603D249DF53d8b1650c762c4df316013Dce840 before September 28 at 23:59 GMT and we will consider this a whitehat, we will give you 20% of the retrieved amount as a bug bounty, payable as you see fit. Should the funds not be returned by then, we will have no choice but to pursue accordingly with everything in our power with the appropriate authorities to retrieve our funds.

 Then came a reply: 

 What about normal people who you have mev'ed and literally fucked them? Will you return them? Return the funds to all people before September 28 at 23:59 GMT and we will consider this a whitehat, we will give you 1% of the retrieved amount as a good heart sign, payable as you see fit. Should the funds not be returned by then, we will have no choice but to pursue accordingly with everything in our power with the appropriate authorities to retrieve our funds.

 Last year, in “Return to the Dark Forest”, we wrote: 

 Frontrunning is vampiric. It feeds off weaker participants, while conflicts with other bots push gas prices to unusable levels. Most of the time, frontrunners win…

 But not this time… 

 MEV bots act on the boundary of “code is law”. 

 In the PvP arena that is Ethereum’s Dark Forest, sometimes you win and sometimes you lose. 

 Despite the fact that the funds were never returned to their original owner, it’s nice to see such a prompt display of on-chain karma.

 As Bert Miller wrote on Twitter:

 Bad code, great content 

 Which would make a great tagline for rekt.news… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
