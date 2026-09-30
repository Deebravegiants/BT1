# [C] Whale Hunter's Payday exploit: When phishing for whales, sometimes you land a big one

## Summary
Severity: Critical
Target: Whale Hunter's Payday
Loss: $55,470,000
Published: 08/20/2024
Source: https://rekt.news/whale-hunters-payday
Type: rekt-postmortem

## Details
## Whale Hunter's Payday

 Wednesday, August 21, 2024 REKT - Phishing 

 read this article also in : zh 

 When phishing for whales, sometimes you land a big one. 

 A crypto whale found themselves $55.47 million lighter after falling victim to a sophisticated phishing attack targeting their Maker vault. 

 On August 20, ZachXBT noticed something phishy , when a whopping 55.47 million DAI had vanished from a single wallet.

 The whale, perhaps sensing something was amiss, attempted to withdraw their funds to safer waters.

 But it was too late, the ownership had already changed and the transaction failed.

 A digital fortune had evaporated in the blink of an eye, serving as a very expensive lesson in the dangers lurking in crypto's deep waters. 

 How did this whale fall for such an elaborate trap and end up on the phisher's menu? 

 Credit: ZachXBT , CertiK , The Block , Lookonchain 
 The attack played out like a masterclass in digital sleight of hand. 

 Our unfortunate whale inadvertently signed an unknown transaction, unknowingly handing over the keys to 55.47 million DAI.

 The attacker, armed with control of the victim's externally owned account (EOA), set their sights on the real prize: a Maker Vault.

 With the finesse of a seasoned angler, the attacker transferred ownership of the victim's DSProxy, a smart contract allowing multiple calls in a single transaction, to their own address.

 This clever maneuver allowed them to change the vault's owner address and withdraw 55,473,618 DAI stablecoins directly into their wallet. 

 Hook, line and sinker. 

 Victim's address: 
 0xf2B889437F243396b29E829908b5d8ebE2e13048 

 Phishing address: 
 0x0000db5c8B030ae20308ac975898E09741e70000 

 Attacker's withdrawal address: 
 0x5D4b2A02c59197eB2cAe95A6Df9fE27af60459d4 

 The main heist transaction: 0xf70042bf3ae7c22f0680f8afa078c38989ed475dfbe5c8d8f30a50d4d2f45dc4 

 Lookonchain reported that the attacker had already begun laundering their ill-gotten gains.

 By the time of reporting, 27.5 million DAI had been swapped for 10,625 ETH.

 In these murky waters, even skilled crypto divers struggle to retrieve what's been lost to the depths. 

 Will the remaining funds be recovered or are they destined to sleep with the fishes? 

 This incident serves as another stark reminder of the dangers lurking in the crypto depths. 

 Phishing attacks continue to be a preferred method for malicious actors, with CertiK reporting nearly $498 million lost to such attacks in the first half of 2024 alone. 

 Jingyi Guo, an analyst at Blocksec, highlighted the likelihood that the victim had signed a phishing transaction, given their failed attempts to invoke the DSProxy after the ownership change.

 One errant click is all it takes and it can cost you dearly. 

 As the crypto seas become increasingly treacherous, users are urged to implement stronger security measures. 

 Multi-factor authentication, hardware wallets and a healthy dose of paranoia are becoming as essential as a life jacket on a sinking ship.

 For now, this whale's tale serves as a cautionary story for all who swim in these waters.

 The next time you're about to sign a transaction, remember that there's always a bigger phish out there and it might just be waiting for you to take the bait.

 In the grand ocean of crypto, even the mightiest whales aren't safe from a well-crafted lure. 

 As phishing attacks evolve and predators grow bolder, is there any safe harbor left in the turbulent seas of crypto? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
