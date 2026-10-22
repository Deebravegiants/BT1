# [C] Gala Games exploit: Possible hacker seized control of an admin address to mint a whopping 5 billion GALA tokens worth $216 million, rapidly offloading 592 million tokens

## Summary
Severity: Critical
Target: Gala Games
Loss: $216,000,000
Published: 05/20/2024
Source: https://rekt.news/gala-games-rekt
Type: rekt-postmortem

## Details
## Gala Games - Rekt

 Tuesday, May 21, 2024 Gala Games - REKT 

 read this article also in : zh 

 Possible hacker seized control of an admin address to mint a whopping 5 billion GALA tokens worth $216 million, rapidly offloading 592 million tokens for $21.8 million in ETH before Gala Games could blacklist the rogue address. 

 Devops199fan noticed that someone minted 5 billion GALA tokens and had been dumping them in batches of 100 ETH on 0xProject . 

 Gala Games reported the exploit as an isolated incident a few hours later, stating that they are working closely with law enforcement to investigate the individuals behind the breach.

 After catching the exploit, the Gala team used a blocklist function to block the hacker to further mitigate the damage. 

 A year earlier, Gala Games had given itself the ability in the V2 contract to blocklist wallets, looks like it came in handy. 

 Benefactor from Gala noted that the ETH contract for GALA is secure and under the protection of a multi-sig wallet and was never compromised.

 Going on to state “we believe we have identified the culprit and we are currently working with the FBI, DOJ and a network of international authorities.”

 Off all the days to fall into a FUD trap. Just before the incident, Bloomberg Intelligence analyst Eirc Balchunas raised his odds of the Securities and Exchange Commission greenlighting the products to 75% from 25% and the market went on a moon mission . 

 Bucking the uptrend seen in other tokens following news of a possible Ethereum ETF approval, GALA's initial plunge of around 20% stood in stark contrast to the broader market rally. 

 As investors grappled with the implications of the exploit, fears surrounding the security breach led to a sell-off that saw GALA's price fall

 Although the token managed to recover some ground in the ensuing hours, the damage had already been done, with GALA ultimately failing to capitalize on the positive momentum sweeping the rest of the crypto market.

 The day after the exploit, the funds were sent back by the exploiter. 

 Yet the multi-million dollar question remained, who was behind this brazen attack on Gala? 

 Credit: The Vulture Trade , Gala Games , Hacken , Benefactor , The Block , Crypto Times , Tay 

 At the core of what could have been a $216 million crypto heist was a critical access control failure. 

 The hacker's path to pillaging Gala Games was paved by allegedly obtaining unauthorized access to an all-powerful admin account on the GALA token contract. 

 According to the attack breakdown by Hacken , the exploit involved an “Access Control” attack vector, where a malicious actor gained control over a dormant MINTER account on the GALA token contract that had not been used for 180 days.

 The attacker minted 5 billion $GALA tokens to a new address dubbed “Gala Game Exploiter”

 Attack transaction: 
 0xa6d90abe17d17743a9cecab84bcefb0fd0bbfa0c61bba60fd2f680b0a2f077fe 

 Followed by the minting, the compromised account sent 2 ETH to Gala Exploiter to possibly cover gas fees for further transactions.

 The exploiter started exchanging the freshly minted GALA for ETH, executing transactions up to 100 ETH.

 GALA for ETH swaps: 

 0xe2ca471124b124831e231fb835778840ad100f97 

 2 hours and 16 minutes later, Gala admins intervened by blocking the exploiter’s account, halting further transactions.

 Blocked Account: 
 0x15129c219a94e24d40541e622757973c0664338f117ff6c4b68d845854b167b9 

 The exploiter transferred all the stolen ETH back to the Minter account.

 Minter Account: 
 0x273c6b54fea8b0d616fb3270698dd4387ec3fefc7b0e290330b4019c35a984b1 

 After that, all the ETH was transferred from the MINTER account to a new externally owned account, possibly by the Gala team to secure the funds.

 Externally Controlled Account: 

 0x16a96053f8e6382a32caa1a4461bf8c500d788019685b803ad3a3194fa5dd290 

 3 days before the exploit, Jason Brink aka Bitbender, announced he was shifting his role at Gala from being President of Blockchain to being an unpaid advisor.

 He also mentioned that a number of people will also be resigning from their positions at Gala to form an external organization, LFG (Let’s Fight Giants).

 The timing is suspicious, especially given some of the shady past of Gala Games. 

 In early 2021, Gala Games lost $130 million after around 8.65 billion GALA tokens were stolen. Eric Schiermeyer, one of the firm's co-founders, sued Wright Thurston, the other co-founder, for allegedly participating in the hack . 

 Thurston then issued his own lawsuit against Schiermeyer claiming that he used company funds for personal use, The Block previously reported .

 The United States Securities and Exchange Commission also sued Thurston and another of these companies in March 2023 for allegedly selling $18 million worth of unregistered securities in the form of GREEN, a cryptocurrency related to a public global decentralized power grid.

 In November of 2022 Gala Games urged its community for calm after misplaced fears of a multibillion-dollar rug pull or hack caused the GALA token to temporarily crash 25.6%. 

 The initial panic, which Gala Games tried to debunk hacking rumors , after a single wallet address appeared to mint over $2 billion in GALA tokens out of thin air.

 Something sounds oddly familiar with the previous minting incident.

 With a track record of unexplained billion-dollar mints and $130 million insider heists, this latest $216 million incident reeks of potential internal sabotage. 

 Is Gala the one playing games here? 

 The shadow cast by the previous incidents at Gala Games, including insider heists and legal troubles, contributes to the aura of suspicion that now surrounds the company. 

 The departure of key figures just days before the latest exploit and the history of unexplained token mints do little to allay fears. 

 In a space where trust is paramount, Gala Games finds itself at a critical juncture, where the next steps it takes could either restore confidence or further erode its standing within the community.

 DWF Labs announced the day after the incident , that they have purchased 28 million $GALA tokens ($1.2M) to stabilize the token's value and express support for Gala. 

 So maybe business will carry on as usual and any suspicions just may get swept under the rug, again. 

 Time in the crypto space feels as if it moves faster than the speed of light at times, attention spans are short and memories even shorter.

 The market's resilience, often bouncing back from scandals and breaches, is a testament to the robust enthusiasm for the blockchain space.

 Will Gala emerge stronger and more secure, or will it become a cautionary tale? 

 Only time will tell if these red flags are truly just coincidences or harbingers of deeper issues within. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
