# [H] Saga exploit: Saga's Inter-Blockchain Communication protocol lived up to its name, it communicated whatever the attacker wanted it to

## Summary
Severity: High
Target: Saga
Loss: $7,000,000
Published: 1/21/2026
Source: https://rekt.news/saga-rekt
Type: rekt-postmortem

## Details
## Saga - Rekt

 Monday, January 26, 2026 Saga - Validation Failure - IBC 

 read this article also in : 

 Saga's Inter-Blockchain Communication protocol lived up to its name, it communicated whatever the attacker wanted it to. 

 On January 21st, someone taught SagaEVM's bridge a new language: fiction. 

 A helper contract whispered custom IBC messages into the precompile's ear, and the protocol believed every word, minting $7 million worth of Saga Dollar from pure imagination .

 No collateral. No validation. Just vibes and forged payloads.

 The attacker redeemed their freshly printed stablecoins for actual assets - yETH, yUSD, tBTC - then bridged the loot to Ethereum and converted it to 2,000+ ETH before Saga could hit the emergency brake at block 6593800 .

 Saga Dollar crashed 25% and depegged to $0.75 . TVL evaporated from $37 million to $13.6 million .

 Another cross-chain bridge learned that trusting messages without verifying their source is just automated gullibility. 

 When your protocol can't tell the difference between a legitimate deposit and a well-crafted lie, who's really minting your money? 

 Credit: Defimon , Blocksec Phalcon , Saga , CoinTelegraph , DefiLlama , Vladimir S. , CertiK , GoPlusSecurity , Cosmos Labs , coingecko , debank 
 January 21st opened with DefimonAlerts catching smoke . 

 "Saga was reportedly attacked, with a large amount of Saga Dollar (D token) minted. The attacker bridged the stolen assets to Ethereum, swapping part into ETH (2,000+ ETH, worth $6M+) and deploying the rest into Uniswap v4 LP positions (worth $800K+)."

 Blocksec Phalcon confirmed the carnage shortly after , noting the root cause remained unclear while the chain sat frozen mid-investigation.

 Vladimir S. carved deeper into the wreckage , pinpointing the attack vector: "An attacker minted D tokens (Saga Dollar) out of thin air with a helper contract that abused IBC mechanisms with custom messages.

 By crafting custom messages or payloads, the contract bypassed validation in the precompile bridge logic, enabling infinite minting of $D tokens without collateral." 

 CertiK and GoPlusSecurity piled on with their own warnings , publishing the attacker's address and exploit contracts while urging users to stay clear. 

 Saga's official response arrived shortly after : "SagaEVM has been paused at block height 6593800 in response to a confirmed exploit on the SagaEVM chainlet. Mitigation is underway."

 Saga’s follow-up Investigation Update painted a grimmer picture : "The incident involved a coordinated sequence of contract deployments, cross-chain activity, and subsequent liquidity withdrawals."

 Then Cosmos Labs dropped the bombshell : "The issue has been identified as originating from the original Ethermint codebase."

 Not just a Saga problem. An ecosystem-wide vulnerability. Multiple EVM chains built on Ethermint now sitting in the blast radius, with Cosmos Labs quietly reaching out to affected projects and distributing short-term mitigations. 

 What happens when one exploit exposes cracks in the entire foundation? 

## Lost in Translation

 SagaEVM uses IBC precompiles to handle cross-chain messaging. Cosmos talks to EVM through these translation layers. They listen for deposit events and trigger mints accordingly. 

 The attacker taught them to hear things that never happened. 

 One contract built to speak fiction fluently.

 Helper Contract: 

 0x7D69E4376535cf8c1E367418919209f70358581E 

 Custom IBC payloads crafted to look like collateral deposits . The precompile swallowed every fake message whole, no verification that assets actually existed on the source chain. 

 Colt protocol mints $D against deposited collateral . It saw the deposits. It minted the tokens. The code worked perfectly - it just had no idea the deposits were fiction. 

 Freshly printed $D in hand, the attacker moved to cash out. They redeemed their worthless tokens against Colt and Mustang for real collateral: yETH, yUSD, tBTC.

 Yield-bearing assets that were actually backing legitimate positions walked out the door via LayerZero, bound for Ethereum.

 One contract feeding fabricated instructions to a bridge that never learned to ask questions.

 Saga's IBC precompile trusted every message it received. The attacker just told it what it wanted to hear. 

 If your cross-chain architecture can't distinguish authentic events from carefully constructed lies, what exactly is it securing? 

## Cashing Fiction

 The attacker didn't waste time admiring their handiwork. 

 Attacker address: 
 0x2044697623afa31459642708c83f04ecef8c6ecb 

 Minted $D flowed straight into Colt and Mustang . Out came yETH, yUSD, tBTC - real yield-bearing collateral that had been backing legitimate positions minutes earlier.

 LayerZero carried the loot to Ethereum . No complicated routing, no exotic bridges. Just a clean extraction to friendly territory.

 Once on mainnet, the swaps started. 1inch, KyberSwap and CowSwap handled the conversions. Multiple transactions, fees ranging from 0.00007 to 0.0023 ETH per swap. Assembly line efficiency.

 The haul: 2,000+ ETH, roughly $6 million at the time .

 But the attacker wasn't done. Rather than cashing out everything immediately, they parked over $800K into Uniswap v4 LP positions . 

 The liquidity didn't stay put for long. On January 24th - three days after the exploit - the attacker spun up a fresh wallet , set approvals for the Uniswap V4 Position Manager , and moved two UNI-V4-POSM NFTs to cleaner storage. 

 The flagged wallet gets the blacklists. The LP positions keep earning yield under a different address.

 Wallet holding NFTs LP on Debank (Worth $847k on January 26th): 

 0xf891de97fa96839329381743f0d6180fcefe3f64 

 The original attacker wallet now sits empty.

 By the weekend, CertiK traced $6.2 million flowing through Tornado Cash - split across five wallets before hitting the mixer. The blacklist coordination came too late. Only the LP positions remain trackable, quietly earning yield under a cleaner address.

 Attack transactions for the record: 
 0x0c038d70c684b5797ed5b8ac578cf7151ec95f5a1a135cd9d48028f72d0f7a2b 
 0x2651c022e2ebba23032b3f0f82a4d9e7caa0be701620e51851e232aa8e35e054 
 0x1fc886dcacbc3e186941236be0e6a1605348d724c0368e21fbf485cb6157ba8f 

 The blockchain remembers everything. Recovery is another story. 

 Over 6 million laundered. Eight hundred thousand left earning yield in plain sight. A receipt, or a taunt? 

## Manual Override

 Saga killed the engine at block 6593800 . 

 By the time Saga hit the brakes, $7 million had already crossed the bridge to Ethereum and the attacker was knee-deep in DEX swaps. 

 The damage report landed in stages.

 First the acknowledgment - "SagaEVM has been paused in response to a confirmed exploit" - followed hours later by the full picture : $7 million in USDC, yUSD, ETH, and tBTC transferred to Ethereum Mainnet.

 Colt and Mustang protocols caught in the blast radius . The attacker's wallet identified and flagged for blacklisting across exchanges and bridges.

 $D, Saga's flagship stablecoin , cracked under the pressure. Price collapsed to $0.73 - roughly more than a 25% depeg that turned "fully backed" into a punchline. 

 Total value locked evaporated from $37 million to $13.6 million in 24 hours . 

 Saga's marketing had promised "automated" infrastructure where "no need for manual bridges" and validators handle everything seamlessly. The Liquidity Integration Layer was supposed to be liquidity without borders. Turns out it was also liquidity without verification.

 The automation worked exactly as designed. It just couldn't tell the difference between a real deposit and a well-crafted fiction. 

 What didn't break : Saga SSC mainnet kept running, validators stayed honest, there has been no consensus failure, validator compromise, or signer key leakage, and their chainlets remained untouched. The foundation held while the penthouse burned.

 Saga spun up coordination efforts with exchanges and bridges to blacklist the attacker's address - the standard playbook when $7 million sits visible on Ethereum and nobody can touch it.

 The chain stays paused until engineering and security teams finish their investigation. A full post-mortem is being offered once findings are validated. 

 When your selling point is seamless automation, what happens when the seams are the only thing anyone remembers? 

 Saga built a protocol that trusted messages. The messages lied. 

 Seven million dollars walked out the door through an IBC precompile that never learned to verify what it was told. 

 The attack wasn't clever. It was just honest about what the bridge would believe.

 Then came the plot twist: Cosmos Labs confirmed the vulnerability lives in Ethermint's original codebase. Saga was patient zero, but the infection runs deeper. Multiple EVM chains now scramble for patches while Cosmos Labs plays triage nurse to an ecosystem that just discovered its foundation has termites.

 Forge the message, bypass validation, print money. 

 The attack surface isn't the code. It's the trust assumption baked into every message relay that treats "received" as "verified."

 Saga's validators stayed honest. Their consensus held. The foundation was sound - until it wasn't.

 The attacker's wallet sits empty now - $6.2 million through the mixer, $847K in LP positions earning yield under a fresh address, while an entire ecosystem waits for patches and post-mortems. 

 When a single exploit reveals that the vulnerability isn't in one chain but in the shared code beneath dozens, how many more $7 million lessons are waiting to be taught? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
