# [C] Grim Finance exploit: The latest entry onto our leaderboard (#18), was a fork of “Beefy Finance” , offering auto-compounding LP vaults on Fantom

## Summary
Severity: Critical
Target: Grim Finance
Loss: $30,000,000
Published: 12/18/2021
Source: https://rekt.news/grim-finance-rekt
Type: rekt-postmortem

## Details
## Grim Finance - REKT

 Monday, December 20, 2021 Grim Finance - REKT 

 read this article also in : zh 

 Don’t fear the reaper. 

 Grim Finance is rekt. 

 The latest entry onto our leaderboard (#18), was a fork of “Beefy Finance” , offering auto-compounding LP vaults on Fantom.

 After the attack, the project’s initial announcement referred to it as “ advanced ”, however reentrancy vulnerabilities are nothing new.

 The price of $GRIM fell 80% after the attack. 

 Charge DeFi lost 1849 $CHARGE to the same attack vector just hours before…

 Was this a serial attacker? 

 Credit: RugDoc 

 The attack exploited a depositFor() function that hadn’t been protected against reentrancy. 

 This allowed the hacker to loop additional false deposits within the initial call, vastly increasing their share of the vault.

 As shown below, the user is able to choose the deposit token, which is where the attacker inserted their own contract containing the reentrancy deposit loops.

 Example transaction and workflow (Credit: @k3mmio ): 

 1) Grab a Flashloan for XXX & YYY tokens (WBTC-FTM e.g.)

 2) Add liquidity on SpiritSwap

 3) Mint SPIRIT-LPs

 4) call depositFor() in GrimBoostVault with token==ATTACKER, user==ATTACKER

 5) Leverage token.safeTransferFrom for re-entrancy

 6) goto (4)

 7) In the last step on re-entrancy call depositFor() with token==SPIRIT-LP, user==ATTACKER

 8) Amount of minted GB-XXX-YYY tokens is increased in every level of re-entrancy

 9) Attacker ends up holding huge amount of GB-XXX-YYY tokens

 10) Withdraw GB tokens and get more SPIRIT-LP tokens back

 11) Remove liquidity and get more XXX and YYY tokens

 12) Repay Flashloan

 Attacker’s address: 0xdefc385d7038f391eb0063c2f7c238cfb55b206c 

 The Grim Finance team has an ongoing investigation tracking the movement of funds across the attacker’s accounts, and have found links to various CEXs. 

 Further details can be found in the rekt.news Telegram group. 

 Charge DeFi claims they reached out to projects who were using the same code in order to warn of the vulnerability. 

 However, perhaps those messages didn’t have the desired effect. One Discord user tried to claim responsibility for the attack.

 If these messages are to be believed, then at least some of the $30 million stolen will be going to charity. 

 But it will be a Grim Christmas for the unwilling donors. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
