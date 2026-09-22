# [C] Wintermute exploit: The glass is half-empty for Wintermute who have lost 20M OP, worth ~$27.6M at the time of the incident

## Summary
Severity: Critical
Target: Wintermute
Loss: $27,600,000
Published: 06/05/2022
Source: https://rekt.news/wintermute-rekt
Type: rekt-postmortem

## Details
## Wintermute - REKT

 Thursday, June 9, 2022 Wintermute - Optimism - REKT 

 read this article also in : zh 

 The glass is half-empty for Wintermute who have lost 20M OP, worth ~$27.6M at the time of the incident. 

 The funds were supposed to be sent to Wintermute by the Optimism Foundation in an agreement to act as a market maker ahead of the OP token launch.

 But Wintermute provided the address of their multisig on Ethereum as the destination address on Optimism - an address they did not control. 

 According to the Optimism Foundation’s announcement , Wintermute then confirmed receipt of two test transactions, firstly for 1 OP and then for 1M OP , without checking that they had access to the funds.

 The remaining 19M OP were sent shortly after the second test transaction on the 27th May.

 According to Wintermute’s statement , they notified the Optimism Foundation about their error on 30th May.

 The OP launch went ahead regardless on the 1st of June, despite almost 10% of the soon-to-be circulating supply being up for grabs.

 An opportunistic anon seized control of the ownerless funds on 5th June. 

 How did the exploiter gain access? 

 Credit: yoav.eth , kelvinfichter , banteg 

 Once the tokens had been sent, they were sitting out in the open, ready to be taken by anyone who spotted them…

 The hint was the fact that the address corresponded to a Gnosis Safe proxy on mainnet, but had no contract deployed to the Optimism address.

 Nobody could take control of the address as an EOA, that would require the private key.

 However, there was a way to access the funds; anyone could take control of the address by deploying a Gnosis Safe proxy to it. 

 This is not an easy task , however. 

 Wintermute state that:

 After consulting with the Optimism and Safe teams, Wintermute made the assessment that the funds were potentially retrievable, and that nobody other than Wintermute could recover those funds. The assessment was also that it was a high risk retrieval that could only be attempted once and required Safe to support. Retrieval was scheduled for 7th of June. However, the assumption that the funds can only be recoverable by Wintermute proved to be false. 

 As Wintermute’s Gnosis Safe on mainnet had been created back in 2020, it was deployed using an old version of the ProxyFactory contract , which includes the out-of-date create opcode, rather than create2 .

 With create , the deployed proxy address depends only on the ProxyFactory’s address and nonce. This meant that the exploiter could replay deployments on Optimism (setting themself as owner) until the nonce matched the original mainnet deployment and a matching proxy address was created.

 This was eventually achieved after running batched deployments of 162 safes at a time, until the matching address was created in this transaction .

 Exploiter’s address , used to create the adapted ProxyFactory contract , which was funded by Tornado Cash on the 1st June.

 Wintermute’s multisig on Ethereum: 0x4f3a120e72c76c22ae802d129f599bfdbc31cb81 

 Hijacked address on Optimism: 0x4f3a120e72c76c22ae802d129f599bfdbc31cb81 

 So far, 1M OP has been sent to the exploiter’s EOA and sold for 720 ETH, and a further 1M OP was sent to Vitalik’s address.

 The exploiter’s timing is interesting, as pointed out by yoav.eth :

 Funded via Tornado 7 days ago

 Then deployed the contract, waited 4 days, and hijacked wintermute's proxy.

 Why wait 4 days?

 If they were looking to secure their loot, why give Wintermute the extra time to mount a rescue attempt?

 The remaining 18M OP have not yet been dumped, is this down to a lack of liquidity or does the exploiter intend to return the funds?

 Wintermute aren’t banking on it: 

 There is hope that it is a whitehat exploit, in which case the remaining funds are potentially recoverable. However we are currently operating under the premise that it is not the case

 In the meantime, the Optimism Foundation has provided an additional 20M OP to Wintermute to perform their original market making duties.

 Wintermute’s balance sheet aside, there are more wide-reaching concerns raised by this incident. 

 Having almost 10% of the OP circulating supply in the hands of a bad actor is potentially dangerous for Optimism’s governance processes, something the Foundation is well aware of .

 Should this change, the option of “ a network upgrade … to halt the movement of those OP tokens ” would set a worrying precedent.

 Although the mistake was flagged on OP’s launch day, the alert was seemingly ignored by the community. The tweet came hours after the exploiter had funded their address, however, so is unlikely to have been the information to tip-off the incident.

 While replacing the 20M OP won’t be a problem for a giant MM such as Wintermute, the carelessness of this incident is alarming. 

 The funds were sat in an unowned address for 9 days. 

 In an already struggling market, actions such as these make it hard to remain Optimistic.

 If you enjoy our work, please consider donating to our Gitcoin Grant .

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
