# [H] Seneca Protocol exploit: Over $6.4 million was stolen from users wallets on February 28, thanks to the bad tao of Seneca

## Summary
Severity: High
Target: Seneca Protocol
Loss: $6,400,000
Published: 02/28/2024
Source: https://rekt.news/seneca-protocol-rekt
Type: rekt-postmortem

## Details
## Seneca Protocol - REKT

 Thursday, February 29, 2024 Seneca Protocol - REKT 

 read this article also in : 

 Over $6.4 million was stolen from users wallets on February 28, thanks to the bad tao of Seneca. 

 First reported by spreekaway on X, the attack involved a critical approval exploit, affecting users on Arbitrum and Ethereum.

 Roughly 80% of the funds were returned within a day, but the remainder has been transferred to 2 addresses, possibly as a bounty. 

 During the canceled audit contest this past November, a security researcher caught the same bug behind the attack.

 “Seneca is using battle-tested code, publicly verifiable on Seneca's GitHub .” Seneca made this statement on X shortly after abruptly closing their Sherlock audit contest due to potential code licensing issues. 

 Weeks later they went into battle and launched without fear, under the belief that they had enough armor thanks to the audit done by Halborn Security.

 The source of the bug, the Chamber contract, was audited prior to deployment, according to Seneca. To note, some of Halborn’s findings were approval related, this exact issue was not highlighted.

 Clearly the other warriors on the battlefield were up for the challenge, because it only took them less than 2 months to find cracks in Seneca’s armor.

 Post-hack, others in the community claimed they were getting booted from Discord for reporting the bug. 

 Clearly Seneca knew there were issues, but chose the reckless route. 

 Revoke approvals if you were unfortunate to invest in this disaster.

 Ethereum:

 PT-ezETH: 0x529eBB6D157dFE5AE2AA7199a6f9E0e9830E6Dc1

 apxETH: 0xD837321Fc7fabA9af2f37EFFA08d4973A9BaCe34

 PT-weETH: 0xBC83F2711D0749D7454e4A9D53d8594DF0377c05

 PT-rsETH: 0x65c210c59B43EB68112b7a4f75C8393C36491F06

 Arbitrum:

 PT-weETH: 0x11446bbb511e4ea8B0622CB7d1437C23C2f3489b

 stEUR: 0x7C160FfE3741a28e754E018DCcBD25dB04B313AC

 PT-aUSDC: 0x4D7b1A1900b74ea4b843a5747740F483152cbA5C

 wstETH: 0x2d99E1116E73110B88C468189aa6AF8Bb4675ec9

 PT-rsETH: 0x2216E32006BB80d20f7906b88876964F9AF68aFb

 Bad decisions or just another bad protocol? 

 Credit: Crypto Smith , Seneca , Spreek , Beosin Alert 
 The exploit took advantage of a bug in Seneca's code to drain assets from users who had active approvals to certain contracts.

 The attacker used constructed calldata parameters to call transferfrom and transfer tokens that were approved to the project's contracts to the attacker's address. 

 This allowed the exploiter to steal any undeployed LSTs from the user's wallet.

 Contracts couldn’t be paused due to a bad implementation of the pause function. Because the pause and unpause functions are internal , there is no way to call them. 

 The exploiter even stole 50k senUSD from the Seneca’s team’s address . 50K that was approved 33 days earlier , but never deployed. Should we wonder why? 

 Over 1.9k of ETH was stolen involving various LSTs that were swapped for ETH. Currently being held in 3 addresses. 

 Exploiter addresses 1: 0x94641c01a4937f2c8ef930580cf396142a2942dc 

 Exploiter addresses 2: 0x5217c6923a4efc5bcf53d9a30ec4b0089f080ed0 Exploiter addresses 3: 0xe83b072433f025ef06b73e0caa3095133e7c5bd0 

 Example attack tx: 0x9f371267 

 Seneca addressed the exploit a few hours after. Instructing users to revoke approvals. But the damage was already done. 

 A few hours later, Seneca posted an onchain message on X addressing a Whitehat, requesting the funds be returned for a 20% bounty. 

 Shortly after, the hacker returned 1,537 ETH to the Gnosis Safe address and transferred 300 ETH to 2 new addresses.

 Address 1: 0x0C77350C4BDe539FfCee261A149dbc6e6afDA517 

 Address 2: 0xa07c64E55F52AAf5c361321CF01b316eCbddB5A9 

 They claim a post-mortem will be published once all of the information is collected.

 The exploiter's address behind the attack was funded 5 months ago through FixedFloat . It remained dormant, until shortly before the attack was carried out on Seneca.

 Follow the flow of funds :

 Will Seneca do their due diligence or continue the pattern of irresponsibility? 

 The warning signs were there from several in the Web3 security community. Everybody sounded the alarm, except Seneca.

 Seneca acted bulletproof with their battle tested (i.e. forked) code. A team member, in a since deleted Tweet bragged about their pristine code, all while trashing Sherlock in the process. 

 Claiming no legal liability is a nice shady cherry on top of this hot mess. 

 There is a thin line between cockiness and ignorance and Seneca fell face first on one side. Which side do you think it is?

 Maybe they should have spent more time getting their code locked tight instead of marketing a broken project. 

 There is no such thing as having too many eyes on your code. The more audits, contests and security reviews the better.

 The worst case scenario was likely avoided, thanks to the attacker returning most of the funds, but this could have been avoided. 

 If you don’t pay the white hats to try to break your code, they'll be forced to make an example of you.

 But given the way Seneca handled this situation, can you blame them? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
