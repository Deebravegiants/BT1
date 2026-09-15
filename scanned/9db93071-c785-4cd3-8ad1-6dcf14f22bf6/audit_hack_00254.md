# [H] Superfluid exploit: The crypto streaming protocol was hacked at 06:17 +UTC 08/02/22

## Summary
Severity: High
Target: Superfluid
Loss: $8,700,000
Published: 02/08/2022
Source: https://rekt.news/superfluid-rekt
Type: rekt-postmortem

## Details
## Superfluid - REKT

 Wednesday, February 9, 2022 Superfluid - REKT 

 read this article also in : zh 

 $8.7M drained from Superfluid. 

 The crypto streaming protocol was hacked at 06:17 +UTC 08/02/22. 

 Other projects who were using the service for contributor payments or investor escrow contracts suffered negative price impacts as the attacker dumped their native tokens.

 The affected protocols included Mai Finance (QI) , Stacker Ventures (STACK) , Stake DAO (SDT) , and Museum of Crypto Art (MOCA) .

 QI was the worst affected token, dropping initially by almost 80% following the dump, but it has since recovered to ~62% of its pre-hack price.

 Superfluid’s @francescorenzia told rekt.news that the attack was focussed only on the platform’s larger wallet balances. In the time before the vulnerability was patched, the hacker left plenty of ETH, USDC and DAI untouched, presumably because the attacker had “ had enough ”.

 How did it happen? 

 Attacker’s address: 0x1574f7f4c9d3aca2ebce918e5d19d18ae853c090 

 Exploit tx: 0xdee86cae2e1bab16496a49… 

 Assets taken: 

 19.4M QI (pre-hack value of $24M) sold in four transactions for a total of 2.3k WETH (~$6.2M)

 24.4 WETH - (~$76k)

 563k USDC sold for 173 WETH 

 45k SDT - sold for ~17 WETH - (~$54k)

 24k STACK - sold for ~6.2 WETH - (~$19k)

 39k sdam3CRV - Swapped to am3CRV , then to ~44k amDAI 

 1.5M MOCA - 1M of 1.5M sold for 173 WETH (~$500K)

 11k MATIC - Not yet sold

 Total - ~$8.7M

 ~6 hours after the attack, Superfluid patched the bug with help from Mudit Gupta. 

 The patch can be found here. 

 The text below is taken from Superfluid’s own post-mortem. 

 Vulnerability Explanation 

 Superfluid.sol, known as the host contract, is the contract that allows composable Superfluid agreements (ConstantFlowAgreement, InstantDistributionAgreement) in one single transaction, and the composed systems are often called Super Apps.

 However, in order to have a trusted and shared state through the entire transaction between different agreement calls, a concept called “ctx” (a serialized state managed by the host contract) is introduced.

 The “ctx” contains all the context an agreement function needs to know, that includes especially who is the “msg.sender” of the initial call.

 That’s where an unfortunate vulnerability was exploited.

 The attacker was able to skillfully craft the calldata such that the process of serialization in the host contract and succeeding de-serialization in the agreement contract resulted in the agreement contract operating on a context object forged specifically to impersonate other accounts. 

 This mechanism was used in order to create IDA indexes “on behalf” of other accounts and move out their tokens that way.

 The Exploiter Contract: 

 The following exploiter contract demonstrates how the vulnerability could be used to impersonate other accounts to close their open streams.

 In the actual exploit transaction , the attacker used the IDA contract to drain funds from other accounts using the same technique:

 Chain of Function Calls 

 deleteAnyFlowBad 

 The convention to callAgreement is to use the placeholder ctx, so that later agreement solidity code can read it directly as an argument “ctx”.

 To read more about this concept, see About-Placeholder-Ctx . 

 This is where the attacker managed to inject a faked “ctx”, where an arbitrary sender could be set.

 Superfluid.callAgreement 

 In the normal case, Superfluid.callAgreement creates the ctx and puts a stamp on it (stores its hash in a state variable), such that it can be validated using Superfluid.isCtxValid. 

 ConstantFlowAgreementV1.createFlow 

 The agreement then uses AgreementLibrary.authorizeTokenAccess to verify that the calling host contract is authorized to do state modifying calls on the token contract.

 AgreementLibrary.authorizeTokenAccess 

 Once the calling host is authenticated, the agreement would transitively also trust the handed over ctx and decode (de-serialize) it into a memory structure.

 But Fake Ctx! 

 The problem was that as in the exploiting function deleteAnyFlowBad , one can inject a fake ctx.

 After being merged into one bytes object by Superfluid.replacePlaceholderCtx (the Host doesn’t make any assumptions about agreement specific data), the resulting dataWithCtx now contains 2 ctx variants, the legitimate one and the injected one.

 When the agreement contract decodes this data, the abi decoder takes the first (injected) variant and ignores the remaining data which contains the legitimate ctx. 

 In order to solve this, Superfluid added a verification step in the agreement contract:

 ISuperfluid.isCtxValid. This verifies the decoded ctx by comparing its stamp (hash) stored in the host contract.

 This check was already in place for handling ctx data provided by SuperApp callbacks, but was not in place for data handed over by the trusted Host contract.

 Superfluid has reached out to the attacker on-chain and, according to the post-mortem, a $1M bounty remains on the table in exchange for the return of the funds. 

 The team also states that most of the affected accounts have already been refunded, while the larger QI and MOCA losses will be compensated more gradually.

 Although this was not the largest exploit (number 42 on our leaderboard ) , and no user funds were lost, it is notable for the manner in which it affected other protocols.

 The growing area of DAO infrastructure presents more targets for the anonymous attackers who are so prevalent in DeFi.

 The stolen money still sits in the attackers wallet. 

 Will they take the bounty, or leave Superfluid high and dry? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
