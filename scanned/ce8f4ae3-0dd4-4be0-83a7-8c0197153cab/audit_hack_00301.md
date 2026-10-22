# [C] Wintermute exploit: Wintermute have lost over $160M to their second incident this summer

## Summary
Severity: Critical
Target: Wintermute
Loss: $162,300,000
Published: 09/20/2022
Source: https://rekt.news/wintermute-rekt-2
Type: rekt-postmortem

## Details
## Wintermute - REKT 2

 Tuesday, September 20, 2022 Wintermute - Profanity - REKT 

 read this article also in : zh 

 Wintermute have lost over $160M to their second incident this summer. 

 In June, the market maker sent 20M OP tokens to an account that they didn’t control.

 Now, their hot wallet has been compromised, likely through the use of a vanity address, created with the vulnerable tool Profanity.

 The loss was announced by Wintermute CEO Evgeny Gaevoy approximately three hours after the theft:

 We’ve been hacked for about $160M in our defi operations. Cefi and OTC operations are not affected

 We are solvent with twice over that amount in equity left

 The firm’s CEO states that the use of the vanity address was for “ gas savings ” rather than aesthetics… an expensive choice. 

 Last time Wintermute got rekt, the exploiter returned (most of) the funds. 

 Will they stay lucky this time around? 

 Hacker’s address: 0xe74b28c2eAe8679e3cCc3a94d5d0dE83CCB84705 

 Attack contract: 0x0248f752802b2cfb4373cc0c3bc3964429385c26 

 Main attack tx: 0xedd31e2a… 

 Second attack tx: 0xc253450f… 

 The likely cause of the hack was a weakness in the Profanity tool used for creating vanity addresses. Following last week’s revelation of the Profanity vulnerability, $3.3M was drained from various wallets by 0x6AE09A… over the following days.

 Both Wintermute’s hot wallet and DeFi vault contract appear to have vanity addresses, with multiple leading zeros. The hot wallet’s private key was likely compromised and used to drain the vault.

 Though the weak security of Profanity-generated addresses only came into the spotlight recently, the issue was raised on the project’s GitHub back in January.

 As described by Mudit Gupta :

 The vault only allows admins to do these transfers and Wintermute’s hot wallet is an admin, as expected. Therefore, the contracts worked as expected but the admin address itself was likely compromised.

 Around the time that the disclosure happened, Wintermute removed all ether from this admin address which suggests that they realized it might have been vulnerable. However, they forgot to remove the address as an admin from their vault.

 The stolen funds were mostly various stablecoins, totalling $118.4M. The majority of these were deposited into Curve’s 3pool, presumably in an attempt to avoid any blacklisting.

 The exploiter is now the 3rd largest holder of 3CRV with over 13% of the supply. 

 Tornado 3pool? 

 The remaining loot is comprised of 671 WBTC (~$13M) and 6,928 ETH ($9.4M) and a variety of other tokens. At the time of writing, the attacker’s address is worth approximately $162.3M.

 While Wintermute’s statement assures that “ there shouldn’t be a major selloff of any sort ”, certain tokens with smaller marketcaps are exposed to a potential dump, with up to 21% of circulating supply taken in the hack:

- $PRIMATE 21%

- $CUBE 12%

- $NYM 2.44%

- $eXRD 1.93%

- $YGG 1.17%

 The majority of assets haven’t yet been swapped. Could the hacker be looking to negotiate a white-hat reward? 

 Shortly after the news broke, the launch of a honeypot token, WinterMuteInu , was spoofed from the exploiter’s address to capitalise on all those watching for signs of movement. The scammer seeded a Uniswap pool with 35 ETH of liquidity , which has so far accumulated ~ 166 ETH (~ $225k).

 Today’s incident marks the first major hack since the sanctioning of Tornado Cash last month. Assuming Wintermute don’t manage to retrieve the funds, it will be interesting to see how the funds are laundered. 

 Post-Tornado sanctions, the potential use of 3pool as a replacement mixer should be of some concern to all Curve users.

 But for now, stay humble … 

 If you enjoy our work, please consider donating to our Gitcoin Grant .

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
