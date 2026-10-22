# [H] Neodyme: How to Hack a DAO

## Summary
Severity: High
Published: Wed, 24 Jan 2024
Source: https://neodyme.io/en/blog/how_to_hack_a_dao/
Type: security-research

## Details
Jan 24, 2024 ~26 min read 

## How to Hack a DAO 

Authored by: - Robert 

## TL;DR ¶ 

 DAOs add a social layer to the otherwise technical execution of blockchain transactions. By exploiting common misconceptions about how they actually work, attackers can ‘hack a DAO’.

## Introduction ¶ 

 Decentralized autonomous organizations (DAOs) are a fascinating subject unique to crypto.
 Gavin Wood even refers to them as a “force of nature”, 1 as they implement an organization, company, community, or service that cannot be shut down.
Not by the police, nor a court, nor even a nation.

 So let’s put that idea to the test: What can a malicious person do to a DAO? 🦹

 The following ideas stem from research within the Solana ecosystem. In particular, I investigated SPL Governance, Solana’s standard DAO implementation. This is why some ideas may be Solana-specific. However, many of them equally apply to other chains and implementations. I encourage everyone interested in DAOs to keep reading, not just Solana enthusiasts!

## DAOs ¶ 

 If you are familiar with DAOs, feel free to skip this part. For everyone else, I’ll try to keep this brief.

 DAOs are on-chain organizations governed by token holders. 2 Anyone who holds a certain governance token is a member . The DAO itself controls accounts. These accounts can be vaults containing funds, program upgrade authorities, mint authorities, and so on. To use these accounts, DAO members create proposals . A proposal contains a set of serialized transactions and instructions, together with a description. To decide whether the proposal shall be approved and subsequently executed, members have to vote on it. Typically, this is a Yes/No vote. Members with a larger amount of governance tokens have more voting power. Once a proposal has been approved, it can be executed.

 The specific fraction of votes needed to approve a proposal is called threshold . For example, a 50% threshold means that half of the full token supply needs to vote Yes to approve the proposal. Also, there may not be more No votes than Yes votes. Thus, a proposal with a 25% threshold, 30% Yes votes, and 40% No votes is declined. An alternative term is quorum . This is the minimum fraction of total votes needed for a proposal to be acceptable. A proposal with a required 10% quorum, 5% Yes, and 4% No votes would be declined because only 9% participated in the vote.

 One last concept I would like to introduce is vote tipping . Typically, a voting period lasts multiple days, at the end of which the votes are counted. With vote tipping, this period can be ended early when the result is evident. Solana’s SPL Governance implements two versions of vote tipping, early and strict :

 Early vote tipping allows a vote period to end early as soon as one of the options has reached a majority and the threshold is fulfilled. For example, in a 25% threshold DAO with 25% Yes and 10% No votes, the voting period can end right then and there. Using strict vote tipping, however, it could not end yet.

 Strict vote tipping lets the voting period end early only once there is no mathematical possibility for the outcome of a vote to change anymore. In the example above, only 35% (25%+10%) of the votes have been cast, so 65% of the votes are still pending. Since they may still change the outcome, the voting period cannot end yet. However, in an example with 53% Yes and 37% No votes, 90% (53%+37%) of votes have been cast, and only 10% of votes are pending. So even if they all voted No , the outcome of the vote would not change. Therefore, this vote period can end early.

 Image 1: A DAO is like a joint wallet. Membership and voting power are managed by tokens that can be bought. Members can propose actions and vote on proposals. 

 To summarize, a DAO is comparable to a public company where anyone can buy a share and participate in shareholder meetings that follow specific rules.

 There are many more details about DAOs that I will spare you here. If you wish to learn all about how this is implemented on Solana, I can recommend this series of writeups .

## DAOs and Social Engineering ¶ 

 In a DAO, no one should have sole control, as this would defeat the purpose. When someone has an idea for the DAO, they have to create a proposal. This proposal will be voted on, so you’d have to convince other people to vote for it .

 We can safely assume that any proposal benefits the proposer in one way or another. Otherwise, why would they propose it? Furthermore, no sane member would approve anything that would harm their personal assets. They have to be convinced of the contrary: That somehow, this proposal will benefit everyone.

 Combining these ideas we can model DAOs as a game where players convince other players to do something to achieve some kind of gain for themselves.

 That’s kinda the definition of Social Engineering .

 In my daily work as a smart contract auditor, social engineering attacks are often disregarded. On bug bounty platforms, you’ll find that social engineering is out of scope . Instead, we look for highly technical bugs , small mistakes, design errors, misunderstood details. However, in the case of DAOs, I argue that social engineering attacks should be at the focus of our attention.

## Recent Attacks ¶ 

 DAO attacks aren’t new. In fact, one of the first and most prominent hacks in the cryptosphere targeted not just a DAO, but The DAO . 3 In the more recent past, a couple attacks stood out:

 The Tornado DAO attack, 4 which happened in May 2023, gained a lot of attention due to Tornado’s notoriety. The hack itself was simple. The attacker copied an old proposal contract and added a 
```
self-destruct
```
 backdoor to it, which allowed the code to be replaced. In the proposal description, they claimed that the proposal logic was identical. It was a simple backdoored proposal attack.

 The Synthetify DAO attack, 5 which happened in October 2023, exploited an inactive DAO with a mispriced governance token. It used spam to test the waters and create distraction. Then, a backdoored proposal which was made to appear as yet more spam was voted through with no opposition. This attack was unique in that is was carried out over a period of three months.

 The Indexed Finance DAO attack 6 happened in November 2023, again targeting an inactive DAO. In fact, Indexed Finance had been hacked two years earlier, and even though it had recovered functionally, it was abandoned in practice. The DAO, while abandoned, still held some assets in its treasury which turned it into an easy target. However, as the attack was almost completed, the DAO was saved by an incredibly close vote.

## How to Hack a DAO ¶ 

 I categorized my ideas into three buckets: Classic Attacks , Proposal Tricks , and Dirty Voting Tactics .

 Classic Attacks are typical attacks on DAOs that have been seen in the wild before. This would include, for instance, the recent Tornado DAO hack using a backdoored proposal or the Beanstalk hack using a flashloan.

 Proposal Tricks are attacks where a technicality about proposals deceives DAO members. This excludes the normal backdoors already featured in the classic attack category.

 Dirty Voting Tactics are attacks where someone with a significant stake tries to maximise their effectiveness by voting in a certain way.

## Classic Attacks ¶ 

## Flashloans ¶ 

 With flashloans, 7 anyone can borrow huge amounts of tokens, as long as the full amount is returned within the same transaction with a fee. For lenders, this is a low-risk opportunity to earn some interest. Problems arise when someone borrows huge amounts of governance tokens, or other assets to be swapped for governance tokens. If the borrower can use these tokens within the same transaction to vote and pay back the flashloan, trouble brews.

 Image 2: Beanstalk exploiter using an AAVE flashloan to stack BEANs. 

 But it’s not as easy as you may think. To vote, governance tokens are locked up in the contract to prevent that the same tokens are used to vote again from another account. They are locked until the end of the voting period.
Thus, to return the flashloan within the same transaction, the attacker’s vote has to end the voting period early somehow. If the attacker may execute the proposal in the same transaction as the vote, they can use the proposal to withdraw funds from the treasury to pay back the flashloan fee and take the rest of the treasury for themselves.

 To protect against this, DAOs can configure a hold-up time. This is a time delta that defines the waiting period between the end of the voting period and the execution of the proposal. However, this is an insufficient protection, because the attacker may withdraw their tokens at the end of the vote, pay back the flashloan, and front the flashloan fee and swap slippage from their own pocket. If they can be sure that the proposal can be executed after the hold-up-time has passed, they will get this money back soon enough.
That’s why another protection is needed: the ability to cancel succeeded proposals during the hold-up time. Either by council or by another vote, for which a flashloan may be used by the defenders.
A better protection is to disallow voting and withdrawal within the same transaction, even if the voting period ends during this transaction.

## Backdoored Proposals ¶ 

 Proposals have two main sources of information that voters will see:

- The proposal title and description

- The serialized transactions to be executed

 A legitimate proposal will have a title and description that honestly and accurately describes the effect of the proposed transactions. However, there is no guarantee that this is the case: A DAO member may propose a transaction that sends tokens to address A, while writing a description how they will be sent to address B.

 Image 3: TornadoDAO exploiter pretending to use “same logic of proposal #16”, secretly having added a self-destruct function that allowed to change the contract logic. 

 The voters are responsible to ensure that transaction and description match, and that they understand exactly what the effects of the transaction are before voting on it.
Yet, this responsibility is rarely acted on. Oftentimes voters just skim the text and transactions, or just vote according to how the others voted.
Many participants in DAOs aren’t technical enough, or just aren’t aware of every trick in the book that malicious parties may use to hide a backdoor in a proposal.
We can’t really blame them. After all, DAOs shouldn’t be usable only by core-devs and security auditors. 

 So the responsibility lies with the DAO members who are capable of inspecting transactions. As a guideline, here are some red flags to look out for:

- Calling unknown programs: No source code and verifiable build? Recently deployed? This is a problem.

- Calling upgradeable programs: Can you trust the upgrade authority of the called program?

- Needlessly setting accounts as writable: Backdoor might need these accounts writeable.

- Proposals from unknown parties: Obviously.

- Multiple transactions: As we’ll see later, this could be abused.

- Any mismatch in explanation and transactions: Even minor details.

- Anything that’s not easily understood: Proposals should be easy to understand.

## Mispriced DAO Tokens ¶ 

 The net worth of a DAO can be viewed as a sum of its assets minus the sum of its liabilities.
One might think that DAO tokens represent a share of these assets, but this isn’t really the case. If I own 5% of a DAO token, but my nemesis owns 6%, they can cancel out all my votes. If I wanted “my share” of the DAO treasury, I’d have to create a proposal. But if my nemesis votes against any proposal that I create, I can’t retrieve anything. What I need instead, is a controlling share .

 So what constitutes a controlling share in a DAO? Well, technically speaking that would be enough tokens to pass a threshold and to win a proposal vote against any opposition. In a DAO with a threshold above 50%, a contolling share is equivalent to enough tokens to meet the threshold. In any other DAO, with a threshold under 50%, we need to beat any potential opposition, so we need more than 50% in any case.

 That’s a lot of tokens. However, in reality, much fewer tokens might be needed. First of all, oftentimes the DAO itself holds a significant share of its own tokens. These tokens are not used to vote, so we need fewer tokens to beat any opposition. If the treasury holds 80%, anything above 10% would beat any opposition. In addition to that, not every token holder is going to vote every time. Oftentimes, it’s just a few whales participating in every vote. It may be enough to be able to out-vote the typical turnout for the average proposal, which is often fairly low.

 Now the price of the DAO token comes into play. If it’s cheap enough, and there is enough liquidity to buy a controlling share of the DAO, the attack becomes obvious. But let me spell it out for you:

 Let’s assume a DAO with a $100M treasury, and 1B governance tokens ₲. Now let’s say the threshold is 2%, and the market is pricing ₲ at $0.01. Typically, 3-4% of holders vote, and the DAO holds ₲800M itself. To win any vote we need ₲100,000,001. To win a typical vote, we need ₲40M plus a margin of error, let’s say ₲60M. At $0.01, that’s $600,000 investment to get our hands on the $100M treasury. For the actual controlling share of ₲100M it’s still just $1M.

 Naturally, the problem is liquidity.

### Liquefier DAO ¶ 

 All that sounds pretty similar to stocks. Get a controlling share of a company and you control the company and its assets. But there is a significant difference: In crypto, the winner takes it all . If you buy 51% of a company, the 49% owners are still entitled to their shares. But if you own a controlling share of a DAO, you can decide to just take all assets for yourself and let the rest have nothing.

 Now we can take this premise and the fact that liquidity for such a move may be hard to come by, and make a bundle. I call this a 
```
Liquefier DAO
```
.

 So we want to attack ₲ DAO. We create a new DAO, which controls a minting contract. Deposit one ₲, receive one g₲, a new token that represents one deposited ₲. Once enough ₲ is deposited to constitute a controlling share, a proposal in ₲ DAO is created to transfer all funds of the ₲ DAO to the Liquefier DAO. In the Liquefier DAO, another proposal is created to use the accumulated controlling share and approve the transfer.

 In the last step, holders of g₲ can exchange their tokens for shares of the stolen treasury.

 GG.

### Mitigations ¶ 

 The obvious solution to mispricing issues is to get the pricing of DAOs right. To do so, market participants need to get educated about DAO mechanics, as we try to do in this post. This way, we can hope that the market will price DAOs correctly in the future.

## Proposal Execution Tricks ¶ 

 Once a proposal has been approved, it will be executed. Or will it? Turns out it’s not that simple. There are multiple cases to be considered. In the most straightforward scenario, yes — the proposal is simply executed. But what if the proposed transaction can’t be executed? Maybe the proposed transaction has an error and the transaction reverts. Maybe multiple transactions were proposed and they can’t all be executed at once.

 That’s a tricky scenario. Especially the reverting part: When the transaction reverts, this failure cannot be logged on the chain, because then the whole transaction reverts, including the part where the DAO contract is invoked.

 SPL Governance introduced a function to mark an approved proposal as “Executing with errors”, just so this revert can be recorded on chain. The intention is that an external root cause may be fixed, and then the broken instruction can be executed.

 Well, this was not such a good solution. It is impossible to “prove” that you actually tried executing this transaction and it failed. So anyone could just mark an approved transaction as “Executing with errors”, even though it was fine.

 Furthermore, we realized that having a “Executing with errors” proposal that is still executable after it is fixed can be dangerous, because temporary “failures” can be introduced arbitrarily: For instance, by using an SPL token account that has not been created yet. To fix this “failure” at any time, just create the account. The following two attack ideas exploit this kind of feature.

 On the EVM, which has robust revert handling with error messages, a proposal can be made unexecutable by executing an invalid opcode, which will consume all available gas.

## Proposal Premining ¶ 

 When a new DAO is created, for a short period of time, it is everything BUT decentralized. Typically, the initial creator has full control over the DAO, which makes sense, because they need this control to set it up in the first place.
Now, what if they used this moment to create a proposal, vote for it with no opposition, and then make it fail with some blocker they can easily fix any time. For instance, this proposal could mint a ton of governance tokens to themselves.
Then, they go on with the regular business of the DAO creation. Anyone who joins this DAO will just see some failed proposal in the initiation phase, no biggie.

 The possibility to execute approved proposals long after their approval is therefore quite dangerous. The feature to flag a “failing” proposal plays into this attack, as users might not be aware that this doesn’t stop future execution.

 I call this attack “Proposal Premining”, because it reminds me of premining block rewards in the initiation phase of a new blockchain.

 Image 4: A DAO with a premined proposal - can you spot it? 

 Mango DAO implemented a custom wrapper contract to protect against any delayed execution attacks. 8 

## Fake-Failed Proposals ¶ 

 How can regular DAO users abuse the flagging mechanism? Easy, let me draw a scenario:

 A DAO wants to employ a developer to build something for them. That’s quite common. Typically, the developer will create a proposal similar to the following:
 “Pay DevGuy $20k for the development of our new mobile frontend!“ 
So far, so normal. But what if the transaction attached to this proposal is engineered to fail? Once approved, the developer can start the ruse:
They create an identical transaction with a different destination address.
 “Sorry, the destination account had a copy-paste error. Lets try this again!“ 
I believe many DAOs would approve this proposal without much thought. However, once approved, this “developer” can fix the error in the first proposal and receive a double payout.

 So how could a DAO make sure a proposal that has been marked as failing is not such a scheme? Currently the answer is due diligence through a manual review of the proposed transaction. What’s actually needed is a deadline for proposal execution. A temporary workaround could be enforcing the use of a wrapper contract: Instead of calling, say, the token program for a token transfer directly, we call the wrapper contract which calls the token program. But it also adds a deadline for execution within a day or so.

## Program Upgrades ¶ 

 Oftentimes, DAOs are used to control the upgrade authority of some program. But securely performing a program upgrade using a DAO isn’t that trivial . Typically, a program upgrade proposal will contain a call to the Upgrade instruction of the BPF Upgradeable Loader, and potentially an Initialize instruction to set up the newly upgraded program.

 To verify a program upgrade as a member, we have to make sure that the new program is legitimate. It is held in the buffer account. To check its contents, there should be verifiable build instructions that we can follow to replicate the build from source, that we can then compare to what’s inside the buffer account.

 Next, we need to check that the buffer accounts authority has been transferred to the upgrade authority. Otherwise, the account contents could be changed after the vote has passed and before the instruction is executed.

 If both of these things are good, then the upgrade itself is good. But if there is some kind of initialization afterwards, this needs to be checked, too. Particularly, if this initialization happens in a separate transaction, and is permissionless. If both of these are true, an attacker could upgrade the program, and then run a different initialization instruction. However, even if the instruction is permissioned, this could be abused: If it exists in the current on-chain version too and out-of-order transaction execution is allowed, an attacker can first call the initialization instruction with the old program, and then the upgrade instruction, leading to a potentially unexpected state.

## The Perils of Multi-Transaction Proposals ¶ 

 The following might be my favorite part. Sometimes, a proposal wants to do so many things that they don’t fit into the instructions of a single transaction. So, multi-transaction proposals are a thing. But let me warn you: You have to be really careful using them or voting on them.

### Transaction Reordering ¶ 

 The first funny issue that we found is that proposals with multiple transactions don’t enforce an order in which the transactions are executed. Wait what? 

 So I can propose to:

- Add Liquidity to a Pool

- Swap in the Pool

- Remove Liquidity from this Pool

 But execute them last-to-first? Or in a random sequence?

 Yes, absolutely. 

 They might even be executed with some time apart. Furthermore, some transactions might not execute at all, while others will.

 This feature can be useful when creating proposals with multiple transfers where each transfer is a different recipient who needs to sign. But it’s dangerous when abused.

### In-Between Insertions ¶ 

 OK, so no ordering was a bad idea. What if a DAO program enforced execution of transactions in a specific order?

 Well, let’s consider another scenario:

 There are 1000 governance tokens minted so far, owned equally by A , B , C and the Treasury (250 each). They have a 51% threshold with early tipping. 
 A proposes the following 4 transactions:

 “5x token split: Increase total supply to 5000 tokens. Preserve shares. Have a nice weekend :smile:“ 

- Tx1: mint 1000 governance tokens to A .

- Tx2: mint 1000 governance tokens to B .

- Tx3: mint 1000 governance tokens to C .

- Tx4: mint 1000 governance tokens to the Treasury .

 Seems harmless, right? It’s approved quickly.

 But as they are signing their transactions to vote Yes , B and C didn’t realize that they were signing their own death certificate…

 Image 5: NANI?!? 

 Let’s see how A seizes full control over this DAO after this proposal was approved:

- A executes only Tx1 , and suddenly has 1250 tokens, which is 62.5%. (Meanwhile the others still have a combined 750 tokens)

- A creates a new proposal 2 to mint 20000 tokens to A .

- A approves proposal 2 , and executes it with early tipping. A now has 21250 tokens.

- Because A is a good sport, execute the other 3 transactions of proposal 1 .

 End result:

- A : 21250 tokens

- B : 2000 tokens

- C : 2000 tokens

- Treasury : 2000 tokens

### Incomplete Execution ¶ 

 Another variation of the same attack is incomplete execution . If we still assume that we enforce in-order execution, this can be turned into a dagger. Say, we create a proposal which airdrops some tokens and calls a callback or crank on their contract:

- Airdrop tokens to A 

- Call A crank

- Airdrop tokens to B 

- Call B crank

 Now A updates their contract, and the crank instruction fails. They will receive the Airdrop, and B won’t.

## Dirty Voting Tactics ¶ 

 Let’s move on to another class of attacks. For this, we will once again imagine a fictitious DAO. In this DAO, the threshold will be relatively low, 2%. Typically, this threshold has a good reason. Mango has a 2% threshold as explained by Mango Max: 4 
 “Well first the threshold is based on unissued tokens, So 2% is really 20%, Or 10% nowadays. We used to have 20% and stuff would regularly not pass”. 

 So, in such a case, the DAO holds most of its own tokens, and the 2% threshold represents 10% of the actually circulating supply. And if it was set higher, the DAO would have problems getting good proposals to pass.

 But some DAOs may set such a low threshold without holding most tokens within the DAO itself.

 This opens the door for one party acquiring a large enough stake in the DAO so that they can win a proposal if not enough votes against are rallied .

 If the proposal is obviously malicious, other DAO members will vote against it. So the best approach would be a tricky proposal, as described in multiple versions above. But how can the malicious party use their significant stake to their maximum advantage?

## Spamming ¶ 

 The first technique they might employ is spamming. What I mean here, is that instead of just one tricky proposal, dozens, or even hundreds of proposals are created.
The attacker will vote Yes on all of them with some kind of automated script, while the other DAO members will struggle to vote against every single one manually.

 Naturally, this only works if the other DAO members are not able to write their own voting script and distribute it among members in time.

 Luckily, this attack is mostly mitigated by having batch voting in the realms interface, bringing easy mass-rejection to the masses :)

 Another approach to spamming was shown by the Synthetify exploiter. They created harmless spam proposals as a way to test DAO engagement, and by first making spam proposals with no transactions, users might not scrutinize future spam proposals that would contain malicious instructions.

## Last Second Voting ¶ 

 Imagine this: It’s late evening, you notice a sketchy, maybe malicious proposal in your 2% threshold DAO. Panic sets in. But as you look at the current status of the vote, you see that no one voted for it, while 3.4% voted against . Relief. Not just relief, but now you don’t even have to get your ledger from hiding to add your votes - no way this can sway! There’s no market for 3.4% of tokens, and no party owns more than 2% anyways. You can go to sleep.

 Next morning, proposal passed. WTF?

 In the last second, 2% were changed from No to Yes . This was enough to win the proposal, because everyone thought like you and didn’t bother voting. Yikes!

 Such an attack can be mitigated by setting up a cool-off voting period for your DAO. During this period, members can withdraw their votes, or vote No , or veto a proposal. But no more Yes votes are admitted. This way, a sudden last-second sway attack can be recovered from.

## UI Attacks ¶ 

 Another class of attacks targets the interface that members use to get information about a DAO — the UI. These attacks may change how information is shown to users, or abuse the user interface as a way to directly attack users.

## Missing Proposal / Meta-Info Barrier ¶ 

 For assessing the legitimacy of a proposal, it’s important to assess differences between the proposal description and the proposed actions. Both are shown to the user in the UI. But if they’re not separated properly, this can be abused. Let’s take a look at Nouns DAOs custom proposal UI . The proposal text is rendered markdown, including images, links, and so on. The meta-information about the proposed transactions comes right after it, with the same font, and no separation.

 Image 6: Nouns DAO doesn’t have a good proposal-metadata barrier. 

 Realms, on the other hand. has a clear separation of proposal text and metadata. The proposed instructions are kept within a collapsible element, which allows them to be easily distinguished from the user-provided description.

 Image 7: Realms implements a good proposal-metadata barrier. 

 Now, what if someone were to create a proposal ending with a title saying Proposed Transactions , and then linking to wrong transactions. To hide the real meta-information, just add a ton of newlines, or taaaaall transparent images.

## Arbitrary Proposal Links ¶ 

 Many DAOs may want to let proposers add a link to the proposal description. Promoting decentralization. No central platform for proposals. Now this may be a bad idea. What if I supply my own custom proposal platform as the link, but it misrepresents proposal data? Or maybe my server will show different proposal content to different users, maybe by region? In essence, what’s needed is a trusted proposal viewing server, with an open source implementation that users can run locally when they desire decentralization.

 Just including arbitrary markdown with external images might be bad enough. The attacker might use their own server again and serve a different image to different users.

## Summary & Mitigations ¶ 

 As we’ve seen, there are countless ways to attack DAOs. Some of them may target DAO implementations, but most of them target the other users of DAOs. Proposal Execution Tricks still need members to vote for sketchy proposals. Dirty Voting Tactics also depend on the actions of other users. A Liquefier DAO needs a collective of users to achieve its goal. But what’s common between these attacks is that they make it easy for attackers to deceive users.

 I’ve talked to SPL Governance developers about these attacks, and we developed some approaches to fix them. First of all, Flashloans and Last Second Voting can be mitigated with a cool-off period.
 Backdoored Proposals are unfortunately hard to fix, but SPL Governance introduces the notion of signatories , which are trusted parties such as auditors. These signatories confirm with their signature that the description matches the proposed transactions with no backdoors. Furthermore, program upgrades would invalidate active proposals calling these programs.
 Proposal Premining shall be mitigated by introducing a time limit on proposal execution after approval. In addition, the transaction flagging feature will likely be removed, also mitigating Fake-Failed Proposals .
Lastly, multi-transaction proposals are tricky. While we can enforce in-order execution to mitigate transaction reordering , attacks such as in-between insertions cannot be avoided. One approach would be adding explicit warnings in the UI. Lastly, spamming attacks are mostly mitigated by bonds for proposals and mass-voting features in the UI. Further important mitigations are warnings, tool-tips, and more information in the UI. For instance, dangerous proposals that call the UpgradeableLoader Program could be highlighted.

## Monitoring ¶ 

 For serious DAO users, a good monitoring setup is important. It should alert you when new proposals are submitted, a proposal is swayed, when prices change, or when large amounts of DAO tokens are deposited within a short time span. We are not aware of any open-source monitoring solutions at the moment, but it should be relatively easy to set up your own.

## DAO Parameters ¶ 

 It is extremely important to choose your DAO parameters with utmost care. The correct configuration will differ from DAO to DAO, but you should keep multiple factors in mind:

- How large will the share of the most trusted members be?

- How fast will we be reacting to proposals?

- How liquid is the token?

- Should there be a council?

- Use a cool-off period.

## Footnotes ¶ 

## Footnotes ¶ 

- 
 Shin, L. (2022). The Cryptopians: Idealism, Greed, Lies, and the Making of the First Big Cryptocurrency Craze. Hachette UK. ↩ 

- 
 Other forms of DAOs exist: e.g., DAOs using a shares or a reputational system. On Solana, token-based DAOs are the norm. ↩ 

- 
 https://en.wikipedia.org/wiki/The_DAO ↩ 

- 
 https://twitter.com/samczsun/status/1660012956632104960 ↩ ↩ 2 

- 
 https://twitter.com/Neodyme/status/1715149044794655145 ↩ 

- 
 https://twitter.com/functi0nZer0/status/1725956393910280282 ↩ 

- 
 https://chain.link/education-hub/flash-loans ↩ 

- 
 https://github.com/ckamm/governance-instruction-forwarder/tree/main ↩ 

 On this page

 - TL;DR 

- Introduction 

- DAOs 

 - DAOs and Social Engineering 

- Recent Attacks 

- How to Hack a DAO 

- Classic Attacks 

 - Flashloans 

- Backdoored Proposals 

- Mispriced DAO Tokens 

 - Liquefier DAO 

- Mitigations 

- Proposal Execution Tricks 

 - Proposal Premining 

- Fake-Failed Proposals 

- Program Upgrades 

- The Perils of Multi-Transaction Proposals 

 - Transaction Reordering 

- In-Between Insertions 

- Incomplete Execution 

- Dirty Voting Tactics 

 - Spamming 

- Last Second Voting 

- UI Attacks 

 - Missing Proposal / Meta-Info Barrier 

- Arbitrary Proposal Links 

- Summary & Mitigations 

 - Monitoring 

- DAO Parameters 

- Footnotes 

 - Social Engineering 

- DAOs 

- Solana 

 Share:
