# [H] Term Labs exploit: Half an Ether bought a controlling stake, and it was still overpaying

## Summary
Severity: High
Target: Term Labs
Loss: $8,500,000
Published: 8/23/2026
Source: https://rekt.news/term-labs-rekt
Type: rekt-postmortem

## Details
## Term Labs - Rekt

 Wednesday, August 26, 2026 Term Labs - Governance - Rekt 

 read this article also in : 

 Half an Ether bought a controlling stake, and it was still overpaying. 

 On August 23, Term Lab's vaults lost roughly $8.5 million to an attacker who did not need to exploit a defect in the core vault code. 

 A small amount of capital was enough to acquire 90.7% of the ETH Meta Vault’s voting supply and all of the voting supply in five USDC vaults.

 That single deposit handed one wallet total control over all five USDC vaults and roughly 91% of the ETH Meta Vault’s voting supply , a majority built entirely out of everyone else’s absence.

 Six days later, the proposal it had quietly filed became executable on schedule .

 Its opening actions set the Zodiac Delay module’s cooldown and expiration to zero , eliminating the transaction delay that was supposed to slow dangerous actions. 

 What followed was procedure, not improvisation : Capital was recalled from legitimate strategies, and an attacker-controlled strategy contract was added to the vault, assigned an effectively unlimited debt ceiling, and funded with the recalled assets. 

 Approximately 2,843 WETH and 1.68 million USDC were drained.

 Term Labs confirmed the governance exploit.

 At the time of AMLBot's August 23 monitoring update , the consolidated proceeds had not moved. 

 When the only thing standing between a vault and its own governance is a vote nobody bothers to cast, was the timelock ever protecting anyone? 

 Credit: The Block , Pyro , CD Security , PeckShield , Term Labs , AMLBot , Defimon , CertiK , Yearn , crypto.news 
 Defimon caught it first on August 23 , a Decurity monitoring bot posted two transaction hashes and two attacker addresses. 

 Defimon identified the apparent mechanism before Term Labs had spoken : The attacker had "cheaply acquired a majority of a sparsely-held DAO governance token, then passed malicious proposals to seize control of Term's vaults."

 Term Labs responded shortly afterward, without a loss estimate or technical explanation : "We are aware of a governance exploit impacting Term vaults. We will share more details once it has been further investigated."

 CertiK identified the address that held the proceeds and estimated the loss at roughly $8.5 million.

 PeckShield added further tracing , reporting that approximately 2,843 ETH and 1.68 million USDC had been removed, that the USDC had been swapped into DAI, and that the attacker's initial funding appeared to trace to 2 ETH from Tornado Cash. 

 Yearn later said Term’s vault contracts were built on Yearn V3 architecture , but the exploit ran through a custom governance wrapper and did not apply to standard Yearn vault setups. It added that funds in standard Yearn vaults were safe and unaffected. 

 In a later public update, Term Labs said all Term Meta Vaults had been shut down irreversibly and their DAO governance roles revoked ; the shutdown permanently prevented further deposits, while withdrawals remained open.

 It also said its investigation so far indicated that the underlying Term protocol and direct borrowing and lending markets had not been affected.

 By then, third-party monitors had already mapped the principal transaction flows, identified the attackers and consolidation addresses , and publicly estimated the damage .

 Term still had not explained the critical authorization question, how a wallet with minimal economic exposure could acquire effective governance control in the first place. 

 If outside researchers could reconstruct the essential on-chain picture before midday, why did Term's end-of-day update disclose less than the public record had already established? 

## The Master Key

 The vulnerability was not a bug in Term's core vault contracts. 

 It was governance arithmetic, paired with governance authority broad enough to turn that arithmetic into an $8.5 million exit. 

 Term's Strategy Vaults used Aragon TokenVoting , with voting power represented separately from ordinary vault shares.

 Term’s voting token was a wrapper around vault shares . To obtain voting power, users had to deposit into a strategy vault and then opt in by wrapping their shares into the governance token. Depositing alone gave them no voting power. Almost nobody wrapped .

 On the ETH Meta Vault, total voting-token supply was 0.5352 . The attacker held 0.4852, or roughly 90.7% of the supply, after depositing about 0.5 ETH and wrapping the resulting vault shares .

 Across the USDC vaults, governance-token supply was similarly negligible; reporting indicates the attacker held all active voting power in four of the five affected USDC vaults . 

 The formal settings did not look reckless in isolation : A 50% support threshold, 5% minimum participation, and a voting window of just over six days. 

 But thresholds do not create opposition. When a single wallet constitutes nearly all active voting power, every threshold becomes a formality.

 And because the minimum proposer-voting-power setting was zero , opening a proposal required no voting power.

 The proposal was titled “Veto strategy vault parameter change,” using the format the curator used for routine parameter updates : “Vote YES to VETO the curator’s proposed vault parameter changes. Otherwise, the transaction will become executable when this proposal expires.”

 To anyone scrolling through governance, it looked like a normal veto item . 

 Underneath, however, were 17 actions . 

 The first three reconfigured the Zodiac Delay module: They set its roughly seven-day cooldown to zero, set its expiration to zero, and enabled an attacker-controlled executor.

 The remaining actions recalled capital from all four real ETH strategies , added an attacker-controlled strategy deployed under the name “Fixed Recipient WETH Exit Strategy,” set its maximum debt limit to uint256 max, and pushed the vault’s entire balance into it .

 The important distinction is this: Low governance participation made control cheap, but the governance route also had enough authority to reconfigure the mechanism meant to delay dangerous transactions. 

 The same process intended to provide oversight could alter its own restraint. 

 Whether that authority reflected an intentional design choice, a misconfiguration, or a distinct authorization failure remains unanswered.

 The available public reconstruction does not indicate reentrancy , oracle manipulation, or private-key compromise.

 The attacker needed only to notice that governance was effectively unattended, and that the gatekeeper had been given the keys to its own lock. 

 If a delay module can be disabled by the same proposal it is meant to slow, what exactly is it a safeguard against? 

## Nowhere to Go

 The attacker drained the vaults in two transactions roughly 22 minutes apart, using the same governance playbook. 

 At approximately 06:25 UTC on August 23, the ETH Meta Vault proposal became executable . Seconds later, the attacker called executeProposal(). 

 The transaction recalled capital from four existing strategies , registered an attacker-controlled strategy, assigned it an effectively unlimited debt ceiling, and used that strategy to move the recalled WETH out of the vault.

 Approximately 2,841.74 WETH was extracted from the ETH Meta Vault.

 The proposal recalled WETH from four ETH Meta Vault strategies : Shorewoods ETH, August Digital ETH, Parity Prime ETH, and Parity Core ETH

 Proposal Execution Exploit Transaction 1: 0xd354a15b15cb73d30908f411aee3f795ec86737a4d080e9a818ac4d6d3014129 

 At approximately 06:47 UTC, a second attacker wallet executed the same pattern against five USDC vaults in a single transaction , draining approximately 1,679,639 USDC. 

 Proposal Execution Exploit Transaction 2: 0x9f273f9a5a20c2fc957b06bbfa45db486390eede4a7f44fbe1a2eb6744c2e8a0 

 Attacker Wallets: 
 0xa908b3472d76e7744bab0a5911768a4a6300612b 0x686457a7468b9b31c5dba43b1b16077b48520691 

 AMLBot reported that both wallets appeared to have been seeded with roughly 1 ETH from Tornado Cash before the attack.

 That provenance may complicate attribution, but it does not, by itself, identify an operator or establish a link to any particular person or group.

 The USDC was later swapped into DAI. The ETH/WETH and stablecoin proceeds then converged at a single address:

 Consolidation Address: 
 0xD5183d8BfC65a50863C62aF2538198A8288FFc13 

 At the time of the cited monitoring reports , the address held roughly 2,843 ETH and 1.68 million DAI, representing an estimated loss of approximately $8.5 million. 

 Since then, 300 ETH was transferred from the Consolidation Address to another address , then cashed out through Tornado Cash. 

 Wallet used to cash out through Tornado Cash: 

 0xC14007663A5bb9F13d4d2AEE8c6FE9075eF1d83e 

 Tornado Cash Movement: 

 3 Transactions can be seen here 

 For now, most of the proceeds remain consolidated and publicly traceable.

 Whether the first transfer reflects a shift toward laundering, a test of the route, or something else remains unknown. 

 Most of the remaining funds are visible on-chain. That does not make them recoverable. What, then, was the system actually designed to protect? 

## The Governance Gap

 Term's Strategy Vaults were ERC-4626 tokenized vaults built on Yearn V3 infrastructure. 

 Yearn said the attack occurred through Term's custom governance wrapper and did not affect standard Yearn vault deployments. 

 That distinction may mean little to depositors.

 The underlying contracts appear to have executed the actions authorized by the proposal : recalling WETH from four strategies, adding the attacker-controlled strategy, assigning it an effectively unlimited debt ceiling, and transferring the vault’s funds to it.

 The critical failure was not necessarily an unauthorized call into the vault. It was the system's definition of authorization.

 An audit can identify technical flaws, dangerous permissions, and insecure governance assumptions. 

 But an audit cannot make passive tokenholders participate, nor can sound implementation compensate for a governance token whose active voting supply is so thin that meaningful control costs a fraction of the assets it commands. 

 In Term's case, the risk sat above the core vault logic, in who could govern, how cheaply they could obtain control, and whether a single successful proposal could rewrite the controls intended to limit it.

 Term had been here before . In April 2025, a decimal-precision mismatch introduced during an update to Term's tETH oracle caused incorrect pricing and triggered roughly 918 ETH in unintended liquidations .

 Term attributed the incident to operational execution error, rather than a smart-contract exploit. The protocol said it had recovered about 556 ETH, reducing the final protocol loss to 362 ETH ($650k), and that all affected users would be fully reimbursed .

 Its postmortem also committed Term to mandatory third-party validation for critical oracle updates and protocol parameter changes , alongside full governance transparency through public proposals. 

 Sixteen months later, the governance layer, not the price oracle, became the attack surface. 

 After the recent August incident, [Term shut down all Meta Vaults, revoked their DAO governance roles, and permanently closed them to new deposits while keeping withdrawals open.

 The team said its investigation had not found an impact on the core Term protocol or its direct borrowing and lending markets , while stressing that its review was ongoing.

 As of the available reporting, Term had not published a full transaction-level explanation or completed technical postmortem, nor a recovery and reimbursement plan for the reported $8.5 million loss. The attacker's transactions may have executed successfully within the authority the system had granted them.

 That does not make the outcome inevitable, nor does it make remediation impossible. 

 It makes the unanswered question more uncomfortable: If governance could authorize the removal of the safeguards meant to contain governance, what exactly was audited, and what was left to trust? 

 A small amount of capital decided who governed millions in depositor funds. 

 Term Finance did not lose approximately $8.5 million because an attacker discovered a broken line of core vault code. 

 It lost that money because almost nobody was participating in the governance system.

 In five USDC vaults, the attacker held all of the voting tokens; in the ETH Meta Vault , the attacker held 90.7% of the voting supply.

 The proposal that authorized the drain was presented in the same format as the curator’s routine parameter updates , then used its opening actions to disable the mechanism intended to slow it down .

 The attacker needed six days , a routine-looking title that presented the proposal as an ordinary veto item, and a delay module that governance itself had been allowed to reconfigure . 

 Term has since shut down the Meta Vaults, revoked their DAO governance roles , and closed them to new deposits while keeping withdrawals open. 

 As of the available reporting, it had not publicly explained why those safeguards could be altered through the same governance process they were intended to constrain.

 The reported $8.5 million remains notable not because the attacker was uniquely clever, but because DAOs continue to relearn the same lesson at different price points.

 Decentralization on paper is not a security control when participation is absent in practice. 

 If governance can be captured for the price of a few dollars' worth of vault shares and still call itself decentralized, whose vault was it actually protecting? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
