# [C] Ronin Network exploit: Poly Network has been toppled from the top spot

## Summary
Severity: Critical
Target: Ronin Network
Loss: $624,000,000
Published: 03/23/2022
Source: https://rekt.news/ronin-rekt
Type: rekt-postmortem

## Details
## Ronin Network - REKT

 Tuesday, March 29, 2022 Ronin - REKT 

 read this article also in : zh 

 Poly Network has been toppled from the top spot. 

 ~$624M stolen from Ronin Network.

 And nobody noticed for six days. 

 When they did eventually realise, the Ronin team announced that:

 “We discovered the attack this morning after a report from a user being unable to withdraw 5k ETH from the bridge.”

 Imagine how the Ronin team felt when they found out that the bridge had been drained nearly a week earlier.

 The new biggest cryptocurrency hack ever. 

 But will the attacker be able to launder the loot? 

 With the rising popularity of Axie Infinity, Ronin was launched as an Ethereum side-chain in Feb 2021 to provide the fast, cheap transaction throughput necessary for a p2e game to function. 

 In order to maximise TPS, decentralisation and trustlessness were neglected in favour of a Proof of Authority model in which just nine validators put their reputation at stake, rather than processing any power or funds.

 Of these nine validators, a consensus of five is necessary to approve deposits and withdrawal transactions. 

 Four of the validators are operated by Sky Mavis, meaning that in the event of a security breach, just one more signature was needed to control the network. 

 Although the official Community Alert doesn't give details on how the Sky Mavis validators were compromised, it does point out the vulnerability that led to the attacker gaining control of the required fifth signature.

 The attacker was able to gain access to the additional validator due to an arrangement made between Sky Mavis and the Axie DAO in November last year. A gas-free RPC node was established to ease costs for users during a period of heavy network traffic in which the AXS price peaked. 

 This required Axie DAO approving Sky Mavis validators to sign transactions on their behalf.

 Despite the arrangement only lasting until the following month, the whitelist access was never revoked, allowing the attacker who had compromised Sky Mavis validators to use the additional (Axie DAO) signature necessary to approve transactions.

 The attacker then authorised two withdrawals, draining first 173,600 ETH and then 25.5M USDC from the Ronin Bridge contract . The 25.5M USDC were swapped for ETH via other addresses before being returned to the main wallet.

 Perhaps in an attempt to complicate the chase, 6250 ETH have been transferred from the wallet, some of which has since been transferred to FTX and Crypto.com. The address was also initially funded from Binance, but KYC’d accounts are easily acquired.

 The rest of the funds remain in the attacker’s address: 

 0x098b716b8aaf21512996dc57eb0615e2383e2f96 

 This theft will be remembered not just for its size, but for the surreal lack of awareness shown by the Ronin team. 

 It seems unthinkable that their key infrastructure was not monitored, with the only alert coming from a concerned user days later.

 In their official statement , Sky Mavis has said that “ Moving forward, the threshold will be eight out of nine ” validators to approve transactions.

 However this was enacted almost 11 hours before the incident was officially announced. 

 No need to rush when it’s already been almost a week… 

 Although most agree on its importance, decentralisation is sometimes seen as an academic, or moral distraction from the adrenaline of trading and the pursuit of profit.

 This case shows the real importance of decentralisation. 

 Why hadn't the Ronin validator set been expanded further? 

 As we saw with the Wormhole case , when deep pockets stand to lose out, a bailout is no problem.

 Axie is considered the market leader in GameFi, does this incident present that same level of risk to an entire ecosystem?

 If so, who’s bailing out $624M? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
