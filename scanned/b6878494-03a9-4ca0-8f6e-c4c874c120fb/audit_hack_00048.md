# [C] BonkDAO exploit: Nobody hacked BonkDAO, because nobody needed to

## Summary
Severity: Critical
Target: BonkDAO
Loss: $19,300,000
Published: 7/6/2025
Source: https://rekt.news/bonkdao-rekt
Type: rekt-postmortem

## Details
## BonkDAO - Rekt

 Friday, July 10, 2026 BonkDAO - Governance Attack - Rekt 

 read this article also in : 

 Nobody hacked BonkDAO, because nobody needed to. 

 On July 6, 2026, an anonymous wallet spent $4.4 million buying just over one percent of BONK's circulating supply . Then it voted itself the treasury. 

 4.426 trillion BONK , worth roughly $19.3 million at the time , moved out in one transaction , the second the vote closed.

 Seven wallets decided it . Eighteen thousand members didn't show up.

 The proposal behind it, "Sowellian BonkDAO ," had been submitted on June 30 , dressed as reform, promising to "rebuild from the ashes," a full treasury transfer buried underneath the pitch.

 Nothing here broke. The purchase cleared. The vote counted. Quorum held. The code did exactly what it was told to do. 

 When the rules get followed to the letter and the treasury still ends up empty, was this theft, or was this democracy working exactly as designed? 

 Credit: CoinDesk , Lookonchain , ETHNews , Specter , decrypt , QuillAudits , Bonk , BIP #76 , Chainalysis , Preetam , forklog , Tech Times , Chainlink , COIN360 , Taylor Monahan 
 The vote closed at 09:42 UTC on July 6 . The treasury emptied in the same block. 

 QuillAudits had the mechanics within hours : 882.1 billion BONK bought on Bybit and Binance over the prior two days, just enough to clear a 879.95 billion quorum .

 Three yes votes , turnout at 2.9 %, proposal passed.

 Bonk's official acknowledgment landed just over eight hours after the vote closed , a single Twitter post confirming what on-chain sleuths had already mapped in full: A malicious governance proposal, an estimated $20 million gone, exchange wallets identified, law enforcement notified. No transaction hash. No proposal ID. No wallet addresses. The chain had already published all three.

 By the time the post went up , the money had already moved once, and wasn't finished moving yet. 

 Roughly an hour after the drain , the voting wallet started selling , offloading $5.3 million of the BONK it had bought to secure the vote, hours before BonkDAO said anything at all. 

 By mid-afternoon, after the official statement had already gone up, the drained treasury itself had moved again, this time to a second address ending in "eh42" .

 None of the yes-voter rewards ever materialized , despite the proposal's own pitch promising them .

 Specter was already pulling threads the community hadn't gotten to yet , tracing the voting wallets back through shared exchange deposit addresses to names most BONK holders would recognize.

 QuillAudits co-founder Preetam put the technical verdict plainly : No smart contract bug, no private key leak, just $4 million spent by an attacker who followed the rules, passed a proposal, and drained the treasury, where most voters never read past the title .

 Upbit paused BONK withdrawals . Kraken did the same. 

 If the attacker's wallets were visible, the exchange deposits were visible, and the quorum math was public the entire time, what exactly took eighteen thousand people six days to miss? 

## Loaded Gun

 BonkDAO governed itself through Solana's Realms platform , the same SPL Governance front end used by hundreds of Solana DAOs . 

 Token-weighted governance , also known as one token, one vote. Whoever holds the most tokens wins, and nothing in the design asks whether the winner is a community or a single wallet with a plan. 

 The configuration was, in the words of QuillAudits co-founder Preetam, "a loaded gun" : A 1% community vote threshold, an instruction hold-up time of zero seconds, a proposal creation threshold of only 100 million BONK, and direct treasury transfers via Realms.

 Read that middle line again : Instruction hold-up time, zero seconds. The moment a vote passed, the treasury moved. No review window. No time to veto. No time to notice. 

 An anonymous wallet submitted BIP #76 on June 30 , titled " Sowellian BonkDAO. "

 Its listed actions : "Add Metadata," and a transfer instruction moving 4,426,104,450,305 BONK to a wallet the submitter controlled. 

 The proposal for BIP #76 , can still be viewed on Realms .

 Anyone reading past the headline would have caught it in seconds. Nobody did, for six days. 

 Proposal Creator Wallet ( flagged by Specter ): 8xxRdtzsw1CJWfEahViqNjZwh5dYJAdSbBctWwcbycVo 

 Over July 4 and 5, a separate wallet bought the outcome outright , accumulating BONK on exchanges and borrowing the rest through marginfi until it held the 1 percent needed to clear quorum.

 Two voting wallets cast that stake on July 6 : 882.2 billion BONK, 99.87 percent, from one address, and 97.8 million BONK, 0.011 percent, from a second.

 The final tally landed at 882,383,387,283 BONK in favor of, and 710,848,288 in favor against , a 1,241-to-1 margin that just cleared the 879.95 billion quorum .

 Voting Wallet 1 (99.87% of YES): 
 CyEE7oHVDaFJ5xZLbXY3h2Z2uk1VwhTkdy72kPUEtypQ 

 Voting Wallet 2 (0.011% of YES): 
 FQnQYaYe1UiQZiokdDH39ybRbhJYfzzwXSghnA32pWxc 

 There was no code to break here. The proposal system worked precisely as specified, and the specification was the vulnerability. 

 A one percent quorum, a hundred-million-token proposal threshold, and a zero-second timelock, stacked on top of each other, so which single fix would have actually stopped this? 

## BONK 2.0

 The transfer executed as the vote closed, on June 6th , moving 4,426,104,450,305 BONK , worth roughly $19.3 million the moment it left , out of the treasury into the attacker’s wallet . 

 That attacker’s wallet carries a "funded by Bybit" tag on Solscan , a detail visible to anyone who bothered to look before the vote closed, not just after. 

 BonkDAO Treasury: 

 F8FqZuUKfoy58aHLW6bfeEhfW9sTtJyqFTqnxVmGZ6dU 

 Attacker Wallet: 
 9bxWkNf3BtJ6iehq9KbX9uCWMjem4TFiPZ19T2sYJHvQ 

 Treasury Transfer Transaction: 5tPU1srcRcnmibB7KJi2WQ7cK4zuq5iKTMrSCLjq7hvGjuK4KUTmaHfwicixkJa5jZJmp3y98T7r2qecKV5mWw8P 

 Roughly ten hours later, the entire balance had moved again , to a second address ending in "eh42". 

 Second Attacker’s Wallet: 

 EXaJnmrLf7RAKLfn1hehoKX94keKYmvZm5H5zuYVeh42 

 No portion of it reached the eighteen thousand members who never voted. None of it reached the yes voters the proposal had promised rewards to either.

 Nine hours after the drain, the exploiter tested the water with a $188,000 transfer to an exchange , then moved the remaining roughly $19 million into a freshly deployed multisig.

 Chainalysis named the structure "BONK 2.0," governed by three keys : The malicious voter, the exploiter wallet, and a third wallet with financial ties to the voter wallet.

 Not liquidated. Not laundered through a mixer. Parked, under a name that reads less like a hideout and more like a pitch. 

 If the money isn't running and isn't spending, what exactly is a three-key multisig called "BONK 2.0" supposed to become? 

## Cold Trail

 BONK slid double digits over the next day and settled roughly 93 percent below its all-time high . 

 Upbit paused deposits and withdrawals . Kraken did the same. 

 Neither exchange had a specific account to freeze. They just stopped taking bets on where the rest of it might land.

 SpecterAnalyst kept pulling the thread , and it led somewhere colder than a random wallet: Both voting addresses funneled funds to a shared exchange deposit address that, going back to 2023 , had also received transfers from crypto notte's own public wallet and from a wallet Realms founder deanmachine himself had once publicly rewarded in an early governance test game .

 None of it proves who wrote BIP #76 . All of it means the wallets moving BonkDAO's treasury are not, strictly speaking, strangers to Realms. 

 Nobody has been charged. No funds have been frozen.

 Bonk's own statement said law enforcement had been notified and that recovery was underway , the standard language for an investigation with no bug to patch, no stolen key to revoke, and no clear mechanism to reverse a vote that was never illegitimate on-chain.

 The proposal is still there , permanent, exactly as submitted, titled "Sowellian BonkDAO," sitting on Realms for anyone to reread now that it matters. 

 When the exploit itself is a permanent, unremovable part of the public record and the wallets behind it trace back to names inside the ecosystem, what is BonkDAO actually protecting by staying this quiet? 

 BonkDAO didn't get robbed, it got outvoted. 

 $4.4 million bought a majority nobody contested , and that majority moved roughly $19.3 million out through a door the DAO itself had left open for six days straight. 

 No code broke. No key leaked. No auditor missed a thing, because there was nothing here for an audit to catch, only a governance config that treated a whale with a plan the same as a genuine community.

 Taylor Monahan didn't wait for a post-mortem to render her verdict : "Let anyone who buys in (literally) have a say, they said," mocking the entire premise that handing voting power to whoever bought the most tokens was ever going to end anywhere else.

 How is that token weighted governance voting working out?

 The treasury now sits in a three-key multisig , named for a sequel nobody asked for, while the wallets behind it trace back through years of deposit history to names already inside Solana's own governance world .

 Not one of them has answered for it. Nobody has had to.

 Eight hundred-plus DAOs run the same Realms platform on the same 1% quorum math , most with treasuries their own members have never once bothered to check. 

 If a majority can be bought for a fraction of what it controls and cashed in without breaking a single line of code, is BonkDAO the story here, or is it just the first of eight hundred to run the math out loud? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
