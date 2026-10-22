# [H] Summer Finance exploit: Eight months earlier, someone at Summer.fi zeroed an Ark's deposit cap , and the offboarding stopped there

## Summary
Severity: High
Target: Summer Finance
Loss: $6,040,000
Published: 7/6/2025
Source: https://rekt.news/summer-finance-rekt
Type: rekt-postmortem

## Details
## Summer Finance - Rekt

 Thursday, July 9, 2026 Summer Finance - NAV manipulation - Rekt 

 read this article also in : 

 Eight months earlier, someone at Summer.fi zeroed an Ark's deposit cap , and the offboarding stopped there. 

 On July 6, 2026, an attacker turned that unfinished process into $6.04 million , draining two Lazy Summer Protocol vaults inside a single atomic transaction. 

 The mechanics were almost boring by DeFi standards: No reentrancy, no oracle manipulation, no stolen admin key .

 A Silo market capped for removal that October stayed inside the fleet’s NAV calculation , still pricing itself off a valuation that never adjusted after November’s Stream Finance collapse .

 Donate a token the Ark could never actually withdraw . Watch the share price rise anyway. Redeem against everyone else's real liquidity. 

 Three months of quiet wallet funding preceded the transaction that cashed it out in minutes.

 The Guardian Module got its first live test since April , froze what it could reach, and discovered it had no authority at all on one chain .

 Summer.fi framed it as an offboarding gap rather than a code bug . The contracts behaved as designed. 

 When the remedy for a known problem is "set the cap to zero," what was step two supposed to be, and who forgot to schedule it? 

 Credit: Summer.fi , Blockaid , Vladimir S , CertiK , Cyvers , QuillAudits , Odysseus , PeckShield , ChainSecurity , Sherlock 
 Blockaid saw it first on July 6th , while the transaction was still running. 

 "Blockaid's exploit detection system has identified an ongoing exploit on Summer Finance . ~$6M drained so far."

 No hedging, no "developing story" disclaimer, just a number and a link. A follow-up thread landed a minute later with the exploit transaction, the attacker's address, the exploit contract, and the list of affected Lazy Summer contracts , everything a competing security firm would need to start its own trace before Summer.fi had said a word.

 Independent researcher Vladimir S. relayed the alert within minutes.

 CertiK's own detection system fired shortly after, framing the mechanism in blunt terms : A $65.4 million flash loan, used for liquidity manipulation, netting the attacker roughly $6 million.

 Cyvers noted that the attacker's wallet had been funded through FixedFloat on Base before the Ethereum transaction ran.

 QuillAudits published next , pointing to a same-transaction share pricing and sequencing issue rather than an oracle manipulation, careful to distinguish the two before most outlets had bothered to ask which one it was.

 Phylax Systems founder Odysseus went further , framing the root cause as same-transaction vault/Ark accounting plus liquidity manipulation rather than key compromise or admin-role abuse. He also noted that the exploit contract was unverified, while the Lazy Summer contracts it called were verified and behaved exactly as written. 

 Summer.fi took roughly three hours to say anything at all : "We are aware of the reported exploit a little earlier today and are investigating the root cause. The protocol guardians are currently pausing all Vaults across the Lazy Summer Protocol."

 By the time that statement was posted, PeckShield had already named the primary target, LVUSDC, risk-managed by Block Analitica , and flagged something almost comic sitting inside the wreckage : The vault's displayed APY had briefly spiked to roughly 2.08 million percent.

 PeckShield also pointed to the vault's largest post-exploit holder, an address reportedly tied to Torben Jorgensen of UDHC, sitting on close to 8.6 million USDC in a vault that could no longer honor a normal withdrawal.

 Summer.fi's second statement, roughly 11 hours after the first alert, finally used the word most people had been waiting for : "We identified an active exploit affecting the Lazy Summer Protocol earlier today. As a precaution, Guardians have paused all vaults and set deposit caps to zero across networks. The situation is being actively assessed. Please do not interact with the protocol until further notice."

 Three hours of silence, then a security notice telling depositors not to touch a protocol that had already been drained. 

 Several security teams and independent researchers had already reached the same broad conclusion before Summer.fi confirmed it themselves, so what exactly was being investigated for those three hours, the cause or the wording of the statement? 

## The Ark That Never Left

 Lazy Summer vaults price themselves the same way : The vault sums totalAssets() across active Arks, then divides by shares outstanding. 

 In plain terms the vault treated a stale, illiquid position like cash , even after the Ark stopped accepting deposits, it still counted in NAV, so adding more of it inflated paper value without adding real liquidity. 

 That becomes more consequential when one of those Arks can no longer accept deposits but still remains part of NAV.

 Summer.fi's official September 2025 governance recap confirms that the on-chain vote stemming from SIP2.24, "Update ARKs from core protocols on mainnet fleets (USDC/WETH/USDT)" , specifically the proposal to add 2 Arks to LazyVault_LowerRisk_USDC Fleet on mainnet, was published on September 4 and later passed and executed .

 Its deposit cap was zeroed on October 30, 2025 , in response to November's Stream Finance collapse and the xUSD depeg that followed , roughly eleven weeks after onboarding, zeroing a cap blocks new deposits.

 It does not remove the Ark from the active set, and removeArk itself requires the Ark to already hold zero assets , a condition the offboarding never reached. 

 The timing is worth sitting with. Days after that cap hit zero, a Balancer V2 exploit set off its own chain reaction into the Arbitrum USDC vault , one backing Summer.fi’s Arbitrum USDC vault. 

 The affected market inside that vault was the sUSDx ARK , whose caps Block Analitica later zeroed on November 4 before the DAO removed it via SIP2.39 , executed on November 21st .

 Seventeen days, start to finish. No equivalent sweep for the Varlamore Ark turned up in the available public record; it appears to have remained active and priced into NAV throughout.

 From that October 30, 2025 cap date to the exploit on July 6, 2026 , roughly eight months passed with the stale valuation left in place, priced near par, never marked down for the bad debt underneath it .

 Summer.fi's post-mortem goes out of its way to correct the record : This was never a totalAssets() versus withdrawableTotalAssets() bug. Redemptions drain Arks in ascending order of size, so the large, manipulated Ark was sorted last and was not the one that got redeemed first.

 The result is less a broken function than a vulnerable sequence of events. 

 If the accounting worked exactly as designed, was the exploit really in the code, or in the calendar? 

## Two Vaults, One Withdrawal

 The attacker opened with the smaller vault. A near costless deposit and withdraw round trip through the HigherRisk USDC vault moved roughly $398k into its buffer , so the later inflated redemption could be paid from liquid assets. 

 Then came the real move. The attacker flash borrowed more than $65 million in USDC, plus a smaller USDT leg , and deposited roughly $64.8 million into the LowerRisk USDC vault at a true share price near 1.0665 . 

 The stale Silo Varlamore position was then donated directly into its Ark, no shares minted, just a transfer that pushed the vault's reported NAV up roughly 9.5 percent and the share price to 1.1678 .

 Redeeming that position paid out close to $71 million against a $64.8 million deposit , funded not by the donated Ark but by the vault's genuinely liquid Morpho, Spark, and Sky positions , other depositors' capital.

 The loans were repaid, the profit was swapped to DAI on Curve, and the attacker walked with 6,016,754.998 DAI , split roughly $5.64 million from LowerRisk and $0.40 million from HigherRisk .

 None of it required meaningful capital up front. Three months of quiet wallet funding did the real setup , the transaction itself only took minutes. 

 The on-chain trail, for anyone who wants to verify it themselves: 

 Exploit Transaction: 0x0db528c44f23fc7fa4544684a2fab81096450a14aae8bc89f42cd0592d43da12 

 Attacker EOA: 
 0x7BF716167B48CF527725722C6d79494b45B3BDCa 

 Exploit Contract, unverified: 
 0x0514F827C129C16418a0933E03C99A6AF982FC61 

 Attacker’s Intermediary Wallet (used to cash out through Tornado Cash): 

 0x46E09c4D4d20C0474598b4d2fFDd08bdf416eBa7 

 LazyVault_LowerRisk_USDC, the primary vault hit: 0x98C49e13bf99D7CAd8069faa2A370933EC9EcF17 

 LazyVault_HigherRisk_USDC, hit first to prime the buffer: 0xE9cDA459bED6dcfb8AC61CD8cE08E2D52370cB06 

 Flash loan source : 

 Morpho, roughly 65.419M USDC plus 1M USDT

 Final payout to the attacker : 
6,016,754.998 DAI, swapped from USDC.

 The attacker later routed part of the stolen proceeds through an intermediary wallet and into Tornado Cash, depositing repeated 10 ETH and 100 ETH batches , which continued the cash-out trail after the exploit.

 The exploit contract has never been verified . Everything known about its internal logic comes from trace and log behavior against the verified contracts it called. 

 If the exploit could extract value without ever moving the underlying asset, what does that say about the system that priced it? 

## The Guardians Learned Their Limits

 The Guardian Module, a 6-of-8 multisig spanning Ethereum, Base, Arbitrum, and Sonic , got its first live test during the exploit, having previously been used only once, in April, to cancel a malicious governance proposal . 

 It zeroed deposit caps on both DAO managed vaults , paused Ethereum first since that's where the exploited vaults lived, then Base, Arbitrum and Sonic out of caution. 

 Then it hit a wall. On HyperEVM, the pause reverted, the module simply didn't hold the guardian role there . Deposit caps were already zero on that chain, so the vector was blocked regardless , but the gap was real, discovered live rather than in a tabletop exercise.

 The Guardian Module itself traces back to a different incident entirely.

 Block Analitica’s retrospective on the Arbitrum USDC fleet said that , as a risk-curation response to the USDX event, it had already set the sUSDx Silo ARK’s caps to zero on November 4 and was working to limit exposure more broadly.

 SIP0.2 passed three months later , built to close the very gap that had just cost the Arbitrum vault its Silo exposure. It still had no authority on HyperEVM in July . 

 The exploit did not emerge from unaudited code. 

 ChainSecurity's audit of the Summer Earn Protocol, delivered January 14, 2025 , reviewed FleetCommander and the Ark contracts directly, including the Ark removal flow.

 In finding 8.3, “Removal of Arks Can Be DOSed,” the auditors noted that removeArk depends on ark.totalAssets == 0, which can fail if residual dust remains after disembarking or if tokens are sent to the Ark before removal.

 Summer.fi responded that future Arks should have a way to be fully emptied before removal ; the finding was rated Informational and marked Acknowledged.

 Roughly eighteen months later , an Ark got stuck inside that same unresolved gap, though not by the exact mechanism the auditors described. 

 This was not a dusting attack; the asset was never fully removed in the first place. 

 The Ark simply never reached the removal step at all : Capped for offboarding, never fully emptied, still active, still priced into NAV.

 Later audits, by Prototech Labs and Sherlock , were both scoped to the governance package, staking, vesting, the governor, the staked token.

 Their published scope descriptions do not mention FleetCommander or the Arks, so there is no indication in those reports that Ark lifecycle risk was revisited.

 The Foundation multisig swept the donated Silo shares out of the LowerRisk vault hours later , cutting the distorted NAV out of public view and socializing the loss. 

 The attacker then routed part of the stolen proceeds through an intermediary wallet and into Tornado Cash ; Summer.fi said this signaled limited intent to return the funds voluntarily. 

 Not sure if that groundbreaking insight was written by Captain Obvious or meant to be ironic.

 The funding trail Cyvers flagged in the first hour turned out to be worth chasing: Summer.fi reached out to FixedFloat directly with the addresses and transactions initially funded through the exchange.

 Governance now has to decide what to do with roughly $4 million in illiquid capital still tied up in the drained vaults , and whether the exploiter's shares get excluded from reimbursement.

 An audit named the exact door roughly eighteen months in advance and Summer.fi acknowledged it ; the excerpt does not show whether it was later remediated before the incident. 

 How long can an acknowledged finding remain open before it becomes a failure of process? 

 $6.04 million moved through a gap that had been visible since October 2025 . 

 Three months of patient wallet funding did the real work here , not the flash-loaned theater that made the headlines. 

 Donate an asset nobody could withdraw , watch a number go up, redeem against everyone else's money, the mechanism was almost insultingly simple .

 ChainSecurity wrote the warning down in January 2025 , and Summer.fi replied that future Arks would need a way to be fully emptied before removal, then moved on.

 Later that year, on a different vault , the DAO proved it could execute exactly that kind of removal in seventeen days when it chose to. 

 Everything downstream of the exploit worked as advertised : The Guardian Module paused four chains and found it had no authority on a fifth, the Foundation multisig swept the donated Silo shares out of the vault, and the post-mortem arrived with technical honesty.

 An acknowledged finding is not a closed one . A capped market is not a removed one.

 ChainSecurity rated this finding Informational , the lowest severity on the scale. 

 How many other "Informational" findings are still sitting in production, quietly carrying load? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
