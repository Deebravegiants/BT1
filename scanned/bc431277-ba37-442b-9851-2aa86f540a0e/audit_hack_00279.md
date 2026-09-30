# [H] An Un-SOL-ved Mystery exploit: All are inevitable reactions to an indiscriminate attack, where nobody knows who’s safe, and who’s next

## Summary
Severity: High
Target: An Un-SOL-ved Mystery
Loss: $5,300,000
Published: 08/02/2022
Source: https://rekt.news/unsolved-mystery
Type: rekt-postmortem

## Details
## An Un-SOL-ved Mystery

 Wednesday, August 3, 2022 Solana - REKT 

 read this article also in : zh 

 Panic, chaos, suspicion. 

 All are inevitable reactions to an indiscriminate attack, where nobody knows who’s safe, and who’s next. 

 Approximately 8,000 addresses on the Solana network have been compromised, draining a total of ~$5.3M. 

 Shortly after 11pm UTC last night, news began to circulate of wallets being drained , with SOL and USDC transferred directly into exploiter addresses.

 Initially, the possibility of a network-wide bug led to panic over whether this would mean all Solana accounts had been compromised. 

 But as the stolen funds were tallied, it became clear that the scope of the threat was not existential, but still perturbing. And although the exact vulnerability is still to be uncovered, some clues have emerged.

 But fear leads to rumours… 

 …and separating the signal from the noise is no easy task. 

 Credit: OtterSec , CIA Officer 

 Early reports of missing funds from Phantom wallet users were followed by accounts of an identical breach affecting Slope wallets, with mobile users making up the majority of victims. 

 It quickly became established that exploited addresses had been signing the transfers directly, i.e. this wasn’t a simple, but widespread, case of phishing for malicious approvals.

 However, that meant something far more worrying; the private keys to the affected addresses were compromised. 

 Was there a leak in a browser extension? Mobile malware? Others suspected something deeper, such as an ECDSA nonce reuse issue (as in the case of Anyswap , now Multichain), though it seems unlikely that all 8k addresses would have made the 2+ transactions necessary for such an exploit.

 News even broke of a widespread malware attack on GitHub repositories, though was quickly dismissed as coincidental and overblown.

 Each new theory added to the confusion, and as the community battled to make sense of the exploit, the only safe havens seemed to be hardware wallets or even CEXs. 

 And all the while, amid the chaos, the number of drained accounts (currently around 8k) continued to grow. 

 At least one Ethereum address is also known to be affected. Potentially as a result of porting a common seed phrase between the two chains.

 With theories ranging from leaky extensions to a mobile malware epidemic to a bug in the underlying cryptography… it remains to be seen exactly how so many users came to be affected. 

 However, Solana co-founder Anatoly Yakovenko points to an “ iOS supply chain attack ”, affecting users who have their “ key imported or generated on mobile ”.

 In order to help cut through the noise, any affected users should fill out this form . 

 While investigations into the root cause continue, attention has also been directed towards the exploiter addresses.

 One whitehat took it upon themselves to DDOS the attacker , slowing their progress, but causing downtime for block explorers in the process. Another anon even claims to have obtained the exploiter’s info by sending an NFT linked to an image, which logged the IP that sent the request when viewed.

 The four exploiter addresses identified on Solana hold a total of $5,276,392.50 at time of writing: 

 Htp9MGP8Tig923ZFY7Qf2zzbMUmYneFRAhSp7vSg4wxV ($3,618,270.02)

 CEzN7mqP9xoxn2HdyW6fjEJ73t7qaX9Rp2zyS6hb3iEu ($955,601.51)

 5WwBYgQG6BdErM2nNNyUmQXfcUnB68b6kesxBywh1J3n ($446,965.00)

 GeEccGJ9BEzVbVor1njkBCCiqXJbXVeDHaXDCrBDbmuy ($255,555.97)

 This dashboard provides a useful breakdown of the stolen funds, including by token type (50% USDC, 35% SOL, 15% Other) and affected wallets by loss (top 3: $246k, $125k, $100k). 

 While Solana’s appeal has always been focused on ( somewhat exaggerated ) claims of speed and affordability, will such a widespread attack erode users’ trust in the security of the ecosystem?

 Though this incident is unrelated to Solana’s underlying tech, it will be hard to shake the stigma that jumpy retail users will ascribe to the network. 

 The price of SOL did show a noticeable drop around the time the news broke, but there has been no major crash, suggesting that the panic is now fully under control.

 But the cryptosphere is wary, yesterday’s attack on Nomad Bridge was as chaotic in its execution as today’s rumour mill. No surprise, then, that CT (as well as your anonymous author) loves a good conspiracy theory …

 In this wild-west industry, the promise of short term gains often blinds users to the basic tenets of personal security:

 Use a hardware wallet, diversify risks, and don’t go chasing APYs across risky bridges. 

 But is it ever enough? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
