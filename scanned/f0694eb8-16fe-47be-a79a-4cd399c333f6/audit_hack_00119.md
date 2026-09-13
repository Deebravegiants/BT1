# [C] Harmony Bridge exploit: This is the 3rd bridge in the top 10 , and the second drained via compromised private keys

## Summary
Severity: Critical
Target: Harmony Bridge
Loss: $100,000,000
Published: 06/23/2022
Source: https://rekt.news/harmony-rekt
Type: rekt-postmortem

## Details
## Harmony Bridge - REKT

 Friday, June 24, 2022 Harmony Bridge - REKT 

 read this article also in : zh 

 Harmony has hit a bum note. 

 To the tune of $100M. 

 This is the 3rd bridge in the top 10 , and the second drained via compromised private keys.

 Over 14 hours after the first funds began to move, the theft was announced .

 Were nine figures really secured by just two signatures? 

 Credit: RugDocIO , BeosinAlert 

 The Harmony Bridge was secured by a 2 of 5 multisig , of which the following addresses were compromised: 

 0xf845A7ee8477AD1FB4446651E548901a2635A915 

 0x812d8622C6F3c45959439e7ede3C580dA06f8f25 

 The attack vector which allowed the hacker to take control of these addresses remains unknown, though some have speculated that they were hot wallets with private keys kept in plaintext.

 If an attacker managed to gain access to the servers running these hot wallets, they would have access to the two addresses necessary to pass any transactions they like, such as draining $100M from the bridge.

 Exploiter address: 0x0d043128146654c7683fbf30ac98d7b2285ded00 

 Harmony ETH Bridge: 0xf9fb1c508ff49f78b60d3a96dea99fa5d7f3a8a6 

 Harmony ERC20 Bridge: 0x2dCCDB493827E15a5dC8f8b72147E6c4A5620857 

 Harmony BUSD Bridge: 0xfd53b1b4af84d59b20bf2c20ca89a6beeaa2c628 

 Beginning at 11:06 UTC, the hacker sent 13.1k ETH from the ETH Bridge to the exploiter’s address, 5.5M BUSD from the BUSD Bridge and drained the following assets from the ERC20 Bridge:

 The above were sent on to exploiter addresses 2 and 3 , swapped into ETH and returned to the main address, where they remain.

 On BSC, the attacker also took 5k BNB and 640k BUSD which also remain in the BSC address .

 The flow of funds can be seen in Peckshield’s graphic below: 

 Since the hack, the number of signers has been updated to 4 .

 Too little, too late. 

 Since the leaderboard-topping Ronin incident, in which keys to 5 of 9 validators were compromised, there has been much talk of the sophisticated spearphishing campaigns ascribed to the Lazarus group. 

 With threats like these known to be relentlessly targeting cryptocurrency projects, the fact that another entire network’s official bridge could be drained by compromising just two addresses is far from acceptable.

 Not only should the other cases have set the alarm bells ringing, but in early April @_apedev specifically called out the Harmony bridge’s precarious security situation. 

 How did the devs overlook, and then ignore, such lax security for securing 9 figures of users’ funds?

 Harmony always struggled with attracting users.

 After this attack, and with market sentiment at all time lows, is this the final encore for Harmony Network?

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
