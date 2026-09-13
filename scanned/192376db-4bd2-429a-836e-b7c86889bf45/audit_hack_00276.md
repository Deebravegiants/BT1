# [H] TrustedVolumes exploit: $5.87 million , one transaction, four assets drained before most of the security firms had finished typing their alerts

## Summary
Severity: High
Target: TrustedVolumes
Loss: $5,870,000
Published: 5/7/2026
Source: https://rekt.news/trustedvolumes-rekt
Type: rekt-postmortem

## Details
## TrustedVolumes - Rekt

 Thursday, May 14, 2026 TrustedVolumes - Authorization Failure - Rekt 

 read this article also in : 

 $5.87 million , one transaction, four assets drained before most of the security firms had finished typing their alerts. 

 TrustedVolumes, a liquidity provider and resolver operating inside 1inch's Fusion ecosystem, was hit on Ethereum on May 7, 2026, through an authorization boundary failure in a custom RFQ swap proxy the team built and controlled. 

 No zero-day. No stolen keys. Just a public function, open to anyone, that let the attacker register themselves as a valid order signer - and a fill path that never bothered to check whether the signer actually owned what was being transferred.

 CertiK flagged it first.

 Blockaid followed a minute later.

 TrustedVolumes took almost two and a half hours to confirm what everyone watching on-chain already knew. 

 When the entry point is a function anyone could call, is it even fair to call it an attack? 

 Credit: QuillAudits , TrustedVolumes , banteg , CertiK , Blockaid , SlowMist , The Defiant , CoinPaprika 
 CertiK was first - one post, the damage already done: "The attacker registers as an AllowedOrderSigner through a public function, then executes the order to transfer from the victim. Please revoke any approval to the vulnerable contract." 

 Blockaid followed sixty seconds later with more : Victim contract, exploiter address, attack transaction, and a running damage tally of $5.87M across four assets.

 SlowMist posted the root cause breakdown shortly after : "Signature validation checks _allowedSigners[msg.sender][signer] using caller (taker) instead of order's maker as key, allowing registration via registerAllowedOrderSigner for attack contract and execution of forged orders for any maker." Four drains. Unlimited approvals. No victim signature required at any point.

 TrustedVolumes confirmed the exploit more than a couple of hours later , long after the attacker had already converted the stolen assets into ETH.

 TrustedVolumes' response arrived measured, almost corporate in its restraint - a bug bounty email address, wallet links, and an offer of "constructive communication." Nothing about how it happened. Nothing about what comes next.

 Security firms had the mechanics mapped before the team had typed a word. 

 So if the people watching from the outside understood exactly what broke, what was the team looking at from the inside? 

## Sign Here, Anyone

 Three bugs. Chained together in a custom RFQ implementation that TrustedVolumes built , deployed, and handed unlimited access to their own treasury. 

 None of them required sophisticated cryptography to find. One of them required little more than reading the function name. 

 The core failure, what banteg's Foundry reproduction calls an authorization boundary failure , is this: The contract verified who signed an order, but never once asked whether the signer had any right to spend the funds being moved. Authentication and authorization are treated as the same question, when they are two entirely different ones.

 registerAllowedOrderSigner() was permissionless . Any address could call it and register any EOA as an authorized signer for themselves as a maker. No owner check. No access control. The attacker called it, registered their own EOA , and became a "valid" participant in the system in a single transaction.

 From there, the second bug compounded the first. During fillOrder() , the contract verified allowedOrderSigner[order.receiver][signer] - confirming the signer was allowed for the attacker-controlled receiver, not for the inventory , not for the address actually holding the funds.

 The check confirmed the attacker could sign for their own receiver . It proved nothing about who controlled the inventory. 

 The third bug closed the trap. The contract used the taker field as the from address in the token transfer . The attacker set taker = victim. 

 TrustedVolumes' inventory had granted the RFQ proxy unlimited ERC-20 approvals . No signature from the victim required. The proxy pulled directly from TrustedVolumes' own vault on the attacker's instruction.

 Replay protection existed on paper . In practice, saltStatus wrote to one storage key and read from a different one , meaning every one of the four drain calls passed the replay check without friction. The same structural flaw, four times, back to back, in a single transaction.

 Setup cost : One deployed contract, 4 wei USDC seeded as nominal payment - one per order.

 The RFQ structure required the taker to send something to the inventory per fill. So the exploit contract sent 1 wei USDC to TrustedVolumes per drain, a cent-level gesture the contract accepted as a completed trade, while shipping millions in the other direction.

 Banteg's full Foundry reproduction - reconstructed Solidity, D2 flow diagram, on-chain evidence - confirmed every step against a fork of block 25039669. The exploit didn't need the live attacker's signed blobs. Any address with four USDC and fifteen minutes could have run it.

 A public registration function, a signer check against the wrong address, and a replay guard that never fired, if any one of those three had been built correctly, none of this happens. 

 So which one was the real mistake: The bugs, or the missing review that should have caught all of them? 

## Four Calls, One Transaction, and Gone

 Everything happened in a single exploit transaction . 

 Four calls to the fill function , four assets stripped from TrustedVolumes' inventory, all of it executed within a single Ethereum block. 

 1,291 WETH, 206,282 USDT, 16.939 WBTC, and 1,268,771 USDC . Roughly $5.87 million, all out the door in one shot.

 Each drain followed the same script . The attacker's contract called the fill function, the proxy pulled the asset from TrustedVolumes' inventory using its pre-existing unlimited approval , and sent 1 wei USDC to the inventory as the taker's nominal buy payment.

 Four trades, fully executed by the protocol's own logic, each one a forgery the contract had no mechanism to detect . 

 Exploit Transaction (Single tx - all four drains executed here): 0xc5c61b3ac39d854773b9dc34bd0cdbc8b5bbf75f18551802a0b5881fcb990513 

 Attacker EOAs: 

 0xC3EBDdEa4f69df717a8f5c89e7cF20C1c0389100 

 0x61e6301614178A2cA21Bfa0FBB30ABa06ACC2D1c 

 Exploit Contract ( One-shot contract acting as maker/receiver - received the drained funds ): 

 0xD4D5DB5EC65272B26F756712247281515F211E95 

 Vulnerable RFQ Proxy ( TrustedVolumes' custom swap proxy - entry point for the attack ): 

 0xeEeEEe53033F7227d488ae83a27Bc9A9D5051756 

 RFQ Implementation ( Logic contract behind the proxy, where the buggy code lived ): 
 0x88eb28009351Fb414A5746F5d8CA91cdc02760d8 

 TrustedVolumes Inventory Owner ( Held the assets, had unlimited approvals to the RFQ proxy ): 

 0x9bA0CF1588E1DFA905eC948F7FE5104dD40EDa31 

 Once the assets landed in the exploit contract, WETH was unwrapped and the proceeds forwarded to the attacker EOA . 

 The remaining tokens - USDT, WBTC, USDC - followed the same path out. 

 From there the attacker moved quickly to convert and consolidate the stolen assets, the resulting positions sitting visible on-chain while TrustedVolumes was still drafting its confirmation post. 

 The stolen funds sat across two attacker-controlled wallets - TrustedVolumes' own post-exploit accounting put the figure at approximately $6.7M , though the on-chain drain prices totals $5.87M across the four assets .

 Stolen Funds Address 1: 

 0x61e6301614178a2ca21bfa0fbb30aba06acc2d1c 

 Stolen Funds Address 2: 

 0xc3ebddea4f69df717a8f5c89e7cf20c1c0389100 

 The funds moved faster than the response, the conversion happened before the confirmation, and the trail was already cold by the time anyone official said a word. 

 So what does it mean that the attacker knew this infrastructure better than the team defending it? 

## Open For Business, Apparently

 TrustedVolumes broke an extended Twitter silence to confirm they had been drained . their first public post in well over a year. 

 No prior warnings, no security updates, no community posts. Their first words back were an exploit confession and a bug bounty email address. 

 TrustedVolumes stated they were open to "constructive communication regarding a bug bounty and a mutually acceptable resolution" and provided two contact points: tvbugbounty@proton.me and t.me/trustedvolumes .

 Their website lists CeFi, DeFi, API, and About Us sections . The API documentation points nowhere useful - a base URL and a production endpoint, nothing to click on, no architecture overview, no security disclosures of any kind.

 For a protocol operating as a market maker and resolver sitting on top of millions in assets, the public-facing infrastructure amounted to a name, a Proton Mail address, and a docs page with nothing behind it.

 No audit of the vulnerable RFQ proxy has ever been publicly disclosed. 

 The implementation contract was unverified on Etherscan - source code never submitted. 

 The contract was never open-sourced. Both bugs were visible only from bytecode.

 For a contract that held the keys to unlimited approvals over millions in assets, that absence is its own kind of answer.

 The bug bounty line is open . Whether the attacker picks up is a separate question. The invitation is going one way. The funds are going the other.

 April had already set a grim record - $635M gone across 28 separate incidents , the worst month for crypto theft since the Bybit breach in February 2025 .

 TrustedVolumes adds to a running total that the industry keeps promising to take seriously. 

 A docs page with nothing behind it, an unverified contract, well over a year of silence, and a bug bounty email - if this is what operating a multi-million dollar market maker looks like from the outside, what was it ever supposed to look like from the inside? 

 The pattern is simple. Someone built a contract that moved millions, and they may have skipped the security review. 

 A team that went well over a year without a public word, right up until the moment there was nothing left to say except that they'd been drained . 

 An attacker needed a public function, a misaligned authorization check, and a vault with no gate on it. That's what was sitting there. That's what got taken.

 Banteg rebuilt the entire exploit in Foundry in a matter of hours .

 Any address, 4 wei USDC, fifteen minutes - that's the barrier that stood between TrustedVolumes' inventory and anyone paying attention.

 The bug bounty line is open . Maybe the funds will come back. But a negotiated return doesn't fix an unverified contract, doesn't publish a docs page, and doesn't explain well over a year of silence while sitting on millions in assets with unlimited approvals pointed at custom code nobody may have ever reviewed.

 The vectors shift - private keys, oracle manipulation, authorization failures, but the underlying pattern holds - someone built something that moved millions and skipped the part where they asked whether it was safe. 

 If it takes a $5.87 million exploit to prompt a security review, what exactly was the plan before the attacker showed up? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
