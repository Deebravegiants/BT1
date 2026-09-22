# [H] RIP MEV Bot 2 exploit: $2M was lost on Tuesday night as an MEV bot got a taste of its own medicine

## Summary
Severity: High
Target: RIP MEV Bot 2
Loss: $2,000,000
Published: 11/07/2023
Source: https://rekt.news/ripmevbot2
Type: rekt-postmortem

## Details
## RIP MEV Bot 2

 Thursday, November 9, 2023 MEV Bot - REKT 

 read this article also in : 

 The sandwicher has become the sandwiched. 

 $2M was lost on Tuesday night as an MEV bot got a taste of its own medicine. 

 The curious case of crypto-karma was spotted by Spreek , who identified the issue as an unprotected swap function within the bot’s code.

 The incident is reminiscent of when the notorious bot 0xbadc0de got rekt for $1.5M , last year.

 As we wrote at the time:

 MEV bots act on the boundary of “code is law”.

 When it comes to autonomous on-chain predators it’s hard to sympathise.

 Is this a simple case of ‘you win some, you lose some’? 

 Credit: BlockSec , PeckShield , Spreek 

 For all the complexity within the dog-eat-dog world of MEV, the exploit was surprisingly simple. 

 The bot’s code had left a swap function unprotected, which anyone could call. This was exploited to sandwich attack the bot via WETH/WBTC trades on Curve, funded via a $50M flash loan.

 BlockSec explains :

 A bot was attacked due to the lack of access control of a public function 0xf6ebebbb, which could be exploited to manipulate swaps in Curve pools. The loss was ~$2M.

 Hence the attacker could first abuse the flawed function to pump the asset price (e.g., WETH) and then make a reverse swap to make a profit.

 And Peckshield provided a look at the sandwiched swaps:

 The result : 

 Oooof. 

 Attacker address ( funded via Tornado Cash): 0x46d9b3dfbc163465ca9e306487cba60bc438f5a2 

 Attack tx: 0xbc08860c… 

 Victim address: 0x05f016765c6c601fd05a10dba1abe21a04f924a5 

 Whenever large amounts of money move in DeFi, things tend to work out nicely for Curve ( though not always ), and this incident was no exception. 

 The swapping of vast sums necessary to imbalance the pool enough for a viable exploit generated a cool $250k in fees for the protocol.

 0xc0ffeebabe , another bot known for the occasional whitehat exploit-frontrun, also made an appearance in cleaning up the mess.

 Autonomous bots, while constantly controversial, seem to be a necessary evil of a permissionless financial system. 

 And with the juicy tips often paid to validators, many of the ecosystem’s key players are surely happy to tolerate the activities of the Dark Forest ’s most dangerous predators.

 How long until you fall prey, anon? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
