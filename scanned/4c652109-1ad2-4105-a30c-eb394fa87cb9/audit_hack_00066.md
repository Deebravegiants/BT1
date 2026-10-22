# [C] Compound exploit: Last week, a vulnerability was found in the updated Compound Comptroller vault, and ~$80M in excess COMP was wrongly distributed

## Summary
Severity: Critical
Target: Compound
Loss: $147,000,000
Published: 09/29/2021
Source: https://rekt.news/compound-rekt
Type: rekt-postmortem

## Details
## Compound - REKT

 Monday, October 4, 2021 Compound - REKT 

 read this article also in : zh 

 It’s worse than we thought. 
 Last week, a vulnerability was found in the updated Compound Comptroller vault, and ~$80M in excess COMP was wrongly distributed.

 The Compound team tried to minimise the perceived damage, but they knew it could only get worse.

 Now another ~$68.8M has been sent to the vulnerable vault, and even more COMP is being given away.

 How did it go so wrong for Compound? 

 As if the inital loss wasn't bad enough, Compound could not stop a continued attack. 

 Any user could call drip() on Compound’s Reservoir vault, which would refill the Comptroller and allow for even more incorrect COMP distribution.

 The Reservoir accumulates 0.5 COMP per block. At the time of the first incident, it hadn’t been drained in approximately 2 months.

 With over 200k COMP (~$68M) inside the Reservoir, the Compound team could only wait and hope that nobody would discover that the damage was far from done.

 As they waited for Proposal 64 to pass, which contained a fix for the original bug, Robert Leshner and the team had a tense week ahead.

 However, just three and a half days after the initial event, the secret was out , the Comptroller had been refilled , and another $68.8M was sent to the vulnerable vault.

 As Banteg wrote; 

 If you tally the initial $80m, $22m already claimed after the drip and the $45m currently at risk, the bug tallies to $147m.

 Although this was more of a “bank error” than an exploit, it’s only fair that Compound takes a place on our leaderboard , where we can see that this case is not without precedent.

 In the case of the failed Alchemix experiment, we saw the protocol suffer a ~$6.5M loss due to their own mistake.

 Like Leshner, Alchemix appealed for their users to return the funds, however, they were more successful in doing so.

 55% of the Alchemix funds were returned, an amount which currently seems unachievable for Compound.

 It’s no surprise that users are more likely to do the “right thing” when “asked nicely” , rather than threatened with the authorities.

 In Curve Wars , we remembered when Robert Leshner said; 

 Crying to meatspace courts deeply undermines the “code is law” principles that DeFi was founded on.

 If you want courts and politicians to protect and control you, there is “finance”. If you want a system that is resilient, self-sufficient, open, and upgradable, there is DeFi.

 Now we compare those words to his aggressive appeal ;

 If you received a large, incorrect amount of COMP from the Compound protocol error:

 Please return it to the Compound Timelock (0x6d903f6003cca6255D85CcA4D3B5E5146dC33925). Keep 10% as a white-hat.

 Otherwise, it's being reported as income to the IRS, and most of you are doxxed.

 Was this a threat or an offer? Return the 'stolen' money and keep a clean 10%, or pay 40% to the IRS and keep a clean 60%...

 These nonsensical threats might have done more damage to Compound’s reputation than the multi-million dollar loss. 

 Leshner has since apologised for his words, but can his reputation be repaired? 

 It’s still not clear how (or if) the existing legal and financial systems will cope with the new concept that is decentralised finance, but for now... 

 If you truly want DeFi, then you have to accept the responsibility that comes with it. 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
