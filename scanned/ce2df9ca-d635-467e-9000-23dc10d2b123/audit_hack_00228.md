# [H] Safemoon exploit: Yesterday, Safemoon lost $8.9M worth of ‘locked LP’ thanks to a bug introduced in the project’s latest upgrade

## Summary
Severity: High
Target: Safemoon
Loss: $8,900,000
Published: 03/28/2023
Source: https://rekt.news/safemoon-rekt
Type: rekt-postmortem

## Details
## Safemoon - REKT

 Wednesday, March 29, 2023 Safemoon - BSC - REKT 

 read this article also in : zh 

 Not so safe after all. 

 Yesterday, Safemoon lost $8.9M worth of ‘locked LP’ thanks to a bug introduced in the project’s latest upgrade. 

 The attack, which drained the SFM/BNB pool, was announced by the project and its CEO, John Karony , with replies disabled on both tweets.

 A few hours after the attack, the hacker sent a message to the Safemoon: Deployer address, claiming to be MEV bot operator willing to return the funds:

 Hey relax, we are accidently frontrun an attack against you, we would like to return the fund, setup secure communication channel , lets talk

 However, past on-chain activity suggests they are no white knight after all… 

 Even if the team has dodged a bullet this time… 

 …can they be trusted after such a basic error? 

 Credit: Peckshield , MoonMark 

 Just over six hours before the attack, the Safemoon: Deployer address upgraded the token contract to a new implementation . In doing so, the team introduced a vulnerability leading to an astonishingly simple exploit.

 The new code left the burn() function publicly callable, allowing anyone to burn SFM tokens from any address. 

 This allowed the attacker to burn large quantities of SFM held inside the SFM:BNB liquidity pool, vastly inflating the price of SFM tokens in the pool.

 Then, by selling (previously acquired) SFM tokens into the skewed pool, the attacker was able to drain it of BNB liquidity, for a profit of 28k BNB, or $8.9M. 

 Exploit tx: 0x48e52a12… 

 Attacker’s address: 0x286e09932b8d096cba3423d12965042736b8f850 

 The hacker claims to have frontrunned attack and has reached out to Safemoon to negotiate the return of funds, the majority of which have since been transferred to 0x237D where they remain at the time of writing.

 Since its launch two years ago, Safemoon has been beset by scandal. 

 Initially labelled as a pump and dump scheme, Safemoon shillfluencers were later slapped with a class action suit , before Coffeezilla published a series of detailed investigations into what went on behind the scenes.

 The favourite of tiktok investors during the peak of Spring 2021’s BSC hype , Safemoon claimed it was un-ruggable due to locked liquidity, which was topped-up with every transfer of tokens. However, the transfer fees were also criticised as ponzinomics as bagholders were disincentivised to sell.

 At the peak of shitcoin szn , we wrote:

 the shitcoins show no sign of stopping

 The markets have cooled down significantly since then, and it seems hardly believable that some of these projects have managed to survive this far…. 

 Given the vulnerability was introduced by the project’s deployer address, Peckshield (perhaps charitably, or perhaps via Hanlon’s Razor) suggested that admin keys may have been leaked or phished.

 Regardless of whether the funds are in the hands of a blackhat hacker or whitehat MEV frontrunner, the lack of trust in Safemoon from the wider crypto community suggests they’ll unlikely be safe, even with the team…

 Whether a botched rug attempt, or sheer incompetence, this episode is not a good look for a project that was never very highly regarded.

 Despite all the bad press, any remaining soldiers in the SFM army appear to still believe, or are suffering from a bagholder’s case of Stockholm Syndrome.

 Perhaps if they haven’t been put off by now, they never will be. 

 And even if this turns out to be a lucky escape for Safemoon, errors like this don’t bode well for the project’s future. 

 How much longer can Safemoon last? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
