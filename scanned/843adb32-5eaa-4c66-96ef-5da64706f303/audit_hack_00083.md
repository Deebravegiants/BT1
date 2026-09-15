# [H] DeltaPrime - Rekt II exploit: Looks like lightning does strike twice – right in DeltaPrime's already scorched wallet

## Summary
Severity: High
Target: DeltaPrime - Rekt II
Loss: $4,850,000
Published: 11/11/2024
Source: https://rekt.news/deltaprime-rekt2
Type: rekt-postmortem

## Details
## DeltaPrime - Rekt II

 Monday, November 11, 2024 DeltaPrime - Rekt 

 read this article also in : zh 

 Looks like lightning does strike twice – right in DeltaPrime's already scorched wallet. 

 Two months after their $6 million private key catastrophe, DeltaPrime has achieved the dubious honor of a second spectacular security breach. 

 This time, an unchecked input validation flaw has cost users another $4.85 million across Arbitrum and Avalanche chains.

 For a protocol that promises "Delta-grade security," they're racking up losses faster than a gambler with a credit card addiction.

 While DeltaPrime scrambles to pause operations (again) and users watch their funds vanish (again), one has to wonder – is this a case of terrible luck, or terrible security? 

 In an industry where "twice bitten, thrice shy" should be the motto, will anyone stick around for DeltaPrime's next security surprise? 

Credit: Certik , DeltaPrime 
 The attack on DeltaPrime reads like the work of someone who actually bothered to study the "Exploiting Unchecked Inputs" chapter – unlike the protocol's developers. 

 CertiK first spotted trouble as multiple pools on Arbitrum started hemorrhaging funds due to a critical flaw in the periphery adaptor contract.

 Seems someone skipped the "check your inputs" lecture.

 Within minutes, the attacker had drained $750K from Arbitrum – but they were just getting warmed up.

 Their next target? The protocol's Avalanche deployment, where another $4.1M would soon vanish. Different chain, same painful lesson. 

 DeltaPrime, in a rare display of speed, quickly confirmed what everyone already knew: they'd been thoroughly rekt. Again. 

 At this point, they should probably just laminate their "We've Been Exploited" announcement template.

 But how did this overachieving exploiter school DeltaPrime for $4.85 million?

 The exploit combined two vulnerabilities with the elegance of a well-planned heist and the subtlety of a sledgehammer.

 According to CertiK's detailed analysis , here's how DeltaPrime got schooled: 

 The Arbitrum Exploit kicked off our exploiter's masterclass. 

 Attacker Address on Arbitrum: 

 0xb87881637b5c8e6885c51ab7d895e53fa7d7c567 

 A flash loan of 59.9 ETH set the stage, supplied to DeltaPrime like bait in a trap. 1.18 WBTC was borrowed and immediately redirected through a swap adapter to their attack contract.

 Attack Contract on Arbitrum: 

 0x52ee5c0ea2e7b38d4b24c09d4d18cba6c293200e 

 Using DeltaPrime's reward mechanism like a personal ATM, they retrieved their ETH collateral through an arbitrary input vulnerability.

 First Blood on Arbitrum: 

 0x9efe855cd3783462207ff8a3d94dc17a74e2b2f00bf1b4c8a7e0135dae83ab5c 

 The stolen funds were initially aggregated into the following contract before being distributed: 

 0x52EE5c0eA2E7b38D4B24c09D4d18cba6C293200e 

 On Arbitrum, the $753K was split three ways: 

 0x56e7f67211683857EE31a1220827cac5cdaa634C (49.91 ETH)

 0x101723dEf8695f5bb8D5d4AA70869c10b5Ff6340 (16.62 ETH)

 0x21032a57bb6cfed765b7b5543fe00a3831b1325dacd3c42b6e98db033da8f5da (2.96 WBTC bridged to Ethereum)

 Not content with a mere appetizer, our exploiter turned their attention to Avalanche's richer hunting grounds with equal ease and nearly six times the payoff. 

 Avalanche Massacre followed the same recipe. 

 Attacker Addresses on Avalanche: 

 0xd5381c683191EB0999a51567274abAB73a9Df0AD 0xd3d535141831f6bd8b7df92e2ae0463d60af2413 

 The periphery adaptor contract flaw proved just as fatal on a different chain.

 Another $4.1M vanished faster than promises of "guaranteed yields".

 First Avalanche Strike: 

 0xece4efbe11e59d457cb1359ebdc4efdffdd310f0a82440be03591f2e27d2b59e 

 But here’s where this heist took an unexpected turn – rather than rushing off, our enterprising exploiter decided to put the stolen funds to work. 

 On Avalanche, the stolen bounty found a new purpose, generating yield. 

 Farming Operations: 

- 
 $600K of Staked USDC staked through Stargate

- 
 $518K USDC/USDT providing liquidity on LFJ

- 
 4,865 AVAX for good measure

- 
 49.68 WETH.e because diversification is key

- 
 6.34 BTC.b to round out the portfolio

 Stolen Funds on Avax: 

 0xd5381c683191EB0999a51567274abAB73a9Df0AD (465.35 AVAX)

 0xd3d535141831F6Bd8B7DF92E2AE0463D60Af2413 (69,401 AVAX)

 Most exploiters treat stolen funds like a hot potato – tumbling, mixing, and sprinting for the hills faster than a validator during a network outage. 

 Not our ambitious apprentice. They've turned their stolen stash into a yield-farming empire, staking and earning with the confidence of someone who just found a genuine 100x gem (spoiler: they very rarely exist). 

 PeckShield's audits specifically flagged these vulnerabilities – meaning DeltaPrime had two shots at fixing their security and still managed to miss the target.

 Two audits, both explicitly warning about admin key vulnerabilities and input validation issues.

 Yet DeltaPrime chose to keep their crown jewels behind a single EOA instead of the recommended multi-sig setup – like leaving your front door key under the welcome mat after a security consultant told you twice to install a proper lock.

 Peckshield Audit 1 

 Peckshield Audit 2 

 In a space where "audit" has become as meaningful as "guaranteed APY," at least DeltaPrime is consistent – consistently rekt. 

 When your exploiter starts farming yields instead of running, maybe it's time to reconsider your security strategy? 

 While DeltaPrime scrambles to explain their second security disaster in two months, their exploiter is casually farming yields like they're following an alpha caller's medium post. 

 The sheer audacity of staking stolen funds in public protocols suggests either supreme confidence or spectacular foolishness. 

 Then again, when you're dealing with a protocol that's been exploited twice in sixty days, maybe there's not much fear of consequences.

 DeltaPrime's vision of the future seems to involve watching their users' funds evaporate at an increasingly efficient rate.

 With millions now being casually converted into yield-farming positions, the line between "exploit" and "aggressive portfolio management" grows thinner by the day. 

 At this point, DeltaPrime might want to consider rebranding to "DeltaDecline" – or is that too optimistic given their current trajectory? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
