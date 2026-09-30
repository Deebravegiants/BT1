# [H] Bent Finance exploit: This time, it seems, due to structural failure from within

## Summary
Severity: High
Target: Bent Finance
Loss: $1,750,000
Published: 12/21/2021
Source: https://rekt.news/bent-finance
Type: rekt-postmortem

## Details
## Bent Finance - REKT

 Tuesday, December 21, 2021 Bent Finance - REKT 

 read this article also in : zh 

 Another project bent out of shape. 
 This time, it seems, due to structural failure from within.

 Bent Finance is a "staking and farming platform to enhance your curve returns." 

 Over the past few weeks, one address has been bending the rules of the protocol, extracting ~$1.75M before things were straightened out. 

 When the news broke, and the price of $BENT buckled, the team issued a luke-warm warning informing users that rewards had been paused, but no funds had been lost. 

 However, when PeckShield claimed to have identified the exploit as coming from within… 

 …the team was forced to release an update , which could be read as accusations of an inside job: 

 Credit: BlockSecTeam 

 Rather than a technical smart contract manipulation, this case is far more simple.

 Bent Finance cvxCRV contract was updated on Nov. 30, manually adjusting the balance of the exploiter’s address. 

 This assigned the exploiter enormous amounts of rewards, far exceeding the TVL of Bent Finance itself. 

 Despite the exploit being live for almost three weeks, the problem only became clear with Bent Finance’s recent listing on DeBank , when the exploiter’s wallet profile showed the billions of dollars-worth of pending rewards on the platform. 

 Looking at the main wallet’s token transactions , we see a handful of small deposits, followed by some very large withdrawals, one on Dec. 12 (of 263k cvxcrv-f) and another today at 02:45 AM +UTC (of 250k cvxcrv-f).

 The tokens were then sent on to the exploiter’s secondary address , where they were cashed out for CRV, swapped for ETH and sent to Tornado Cash.

 In total, 440 ETH (~$1.75M) has been washed via Tornado Cash between 12/12 and today. 

 The role that DeBank’s listing of Bent Finance played in today’s case and Nansen’s recent $75M raise show the value that these services bring to an increasingly more complex industry. 

 Although on-chain data provides all the necessary information to those with the knowledge (and motivation) to investigate, these tools vastly increase the probability of spotting irregularities in lower profile projects.

 However, in the case of Bent Finance, given the source of the exploit, as well as the team’s response, this looks likely to be an inside job:

 Rug pull or rogue team member? 

 Much bigger hacks have dominated the headlines recently, and incidents such as this will soon be forgotten.

 Maybe that’s what the Bent Finance team is counting on… 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
