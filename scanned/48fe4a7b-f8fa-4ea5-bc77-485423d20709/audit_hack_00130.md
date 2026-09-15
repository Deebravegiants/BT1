# [M] Hypr Network exploit: Yesterday, gaming-focused L2 Hypr Network lost 2.57M HYPR (approx $220k) to a bridge exploit just two days after launch

## Summary
Severity: Medium
Target: Hypr Network
Loss: $220,000
Published: 12/13/2023
Source: https://rekt.news/hypr-network-rekt
Type: rekt-postmortem

## Details
## Hypr Network - REKT

 Thursday, December 14, 2023 Hypr Network - Bridge - REKT 

 read this article also in : 

 What is this, a bridge hack for ants? 

 Yesterday, gaming-focused L2 Hypr Network lost 2.57M HYPR (approx $220k) to a bridge exploit just two days after launch . 

 The incident was quickly identified by a user, and the team warned users that something was amiss, but without initially admitting to an exploit:

 📢 ATTENTION: Do not use the Hypr Network Bridge. The team wants to perform some more tests and do some further audits on the bridge.

 The team’s follow-up statement reassured users that HYPR holders in general were not affected, with losses coming from just two addresses ( the only users to have bridged funds up to that point ).

 However, the token did experience a drop of almost 40% when the proceeds were dumped for 97 ETH, worth approx $220k at the time of writing, the price has since recovered with the market rebound. 

 While we’ve seen plenty of bridges lose funds to compromised keys over recent months, this is the first example of exploited code leading to a bridge hack since last autumn’s BNB bombshell ( unless you count the Shibarium bridge ’s temporary self-rekt in August ).

 Forking code can be risky, especially when devs aren't up to date with issues in the original source. 

 Should developers of a codebase designed to be forked take more responsibility for communications? 

 Or were Hypr simply not paying enough attention? 

 Credit: BlockSec , Hypr Network 

 The Hypr Network is built via OP Stack which allows developers to deploy fully functional L2s, forking Optimism as a template.

 In the Hypr team’s post-mortem thread , they explain that:

 Hypr used the most recent version of the develop branch of the OP monorepo at the time of deployment. Unbeknownst to us, this was not a production-ready branch and at the time contained a critical vulnerability which had yet to be patched.

 The full post-mortem report can be found here . 

 BlockSec summarised the vulnerability as follows:

 The root cause was that the attacker managed to circumvent the 'finalizeERC20Withdrawal' function check by reinitializing the contract, due to the existence of the 'clearLegacySlot' modifier.

 Exploiter address 1: 0x5b8d598b354f5760b2a65f492154e7a3df46d1be 

 Exploiter address 2: 0x3ea6ba6d3415e4dfd380516c799aafa94e420519 

 Attack tx: 0x51ce3d9c… 

 The exploiter was funded from hacker-favourite FixedFloat and, at the time of writing, the stolen ETH remains in the 0x5b8d address. 

 Composability, interoperability and building upon open-source code are elements which allow for many of DeFi’s greatest innovations. 

 But they also mean that a bug in one place can affect multiple protocols across the sector. 

 Communication between teams and staying up-to-date with security conversations across the ecosystem is key for anyone relying on forked code. As BlockSec points out :

 Note that the vulnerability was patched by the OP team after the contract had been deployed.

 This incident underscores the importance of the community working collaboratively to refine the process for releasing security patches, which will undoubtedly benefit us all.

 Hypr’s post-mortem report states that, following consultation, with the OP Labs team:

 [OP Labs] agreed that improvements on their release and communications process

 And, after reassuring users that other OP infrastructure was unaffected, the Optimism Foundation added:

 We encourage developers building projects in production to use releases approved by Optimism governance, which meet the security bar established by the Collective. We're also improving our release comms processes to help ensure it's clearer to projects leveraging the OP Stack.

 As ever, being the first to bridge to a new ecosystem can often lead to lucrative first mover advantages. 

 After a prolonged period of apathy, FOMO is driving a growing desire to try new things as markets begin to heat back up once again.

 Are the potential rewards worth the risk? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
