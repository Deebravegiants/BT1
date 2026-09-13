# [H] Secret Network exploit: $4.67 million left Secret Network on June 10th

## Summary
Severity: High
Target: Secret Network
Loss: $4,670,000
Published: 6/10/2026
Source: https://rekt.news/secret-network-rekt
Type: rekt-postmortem

## Details
## Secret Network - Rekt

 Friday, June 26, 2026 Secret Network - IBC - Rekt 

 read this article also in : 

 $4.67 million left Secret Network on June 10th . It took seven days for anyone to notice. 

 A bridge contract forked from Secret's standard snip20-ics20 implementation in 2023 , with two security checks quietly removed and never replaced , and open-sourced on GitHub the entire time, minted seven different tokens from thin air and redeemed them for real assets in eighteen minutes . 

 No alerting system flagged it. No pause mechanism triggered. No audit had ever been requested for the fork .

 The funds were consolidated, swapped, and split into about 30 transfers , before being deposited at exchanges, all before anyone thought to check the Axelar escrow account.

 The first sign was a failed transaction on June 17th , when a routine cross-chain transfer failed because the escrow account no longer had enough funds. 

 When the only thing that caught a $4.67 million drain was a failed transaction seven days later, where was the monitoring? 

 Credit: Common Prefix , F12 , Secret Network , Axelar Network , Yi , Rarma , Ray Raspberry 
 Nobody found it, it found them. 

 On June 17th at 15:39 UTC , seven days after the June 10th exploit, a routine cross-chain transfer on Axelar failed .

 The error message was routine : “unable to unescrow tokens, this may be caused by a malicious counterparty module or a bug: please open an issue on counterparty module: spendable balance 803200wbtc-satoshi is smaller than 1000000wbtc-satoshi: insufficient funds.”

 More tokens were trying to bridge out of Secret than had ever bridged in.

 Twenty-one minutes later the team confirmed the IBC escrow account for the Secret-SNIP connection had been drained. 

 By 16:48, they had traced it back to seven IBC transactions on June 10th , all to a single wallet. 

 The exploit had occurred seven days earlier. Nothing had flagged it.

 On Secret Network, balances and transaction details are encrypted by default , so the shortfall was not visible on-chain until a June 17 cross-chain transfer failed , and the team then confirmed the IBC escrow account for the Secret-SNIP connection had been drained.

 Security researcher F12 put it plainly on June 19th : "No exploit tx: Secret is a privacy chain, transfers and balances are encrypted, so the hack isn't visible on-chain."

 That seven-day window was not a consequence of the attacker's sophistication. It was a consequence of the environment they chose to operate in. 

 By the time the error message surfaced, the funds had already been consolidated into ETH, split across thirty wallets, and deposited at three exchanges . The window to intervene had long closed. 

 Axelar Network publicly disclosed the incident on June 19th . Their emergency committee disabled the Secret and Secret-SNIP connections.

 According to Common Prefix, Squid removed Secret Network from its frontend .

 Law enforcement was notified .

 Secret Network's privacy protected its users for years. On June 10th, it protected someone else, and nobody knew until the money was already gone. 

 So who exactly bears responsibility for building a monitoring system capable of seeing through the dark? 

## Two Missing Lines

 A fork of Secret's standard snip20-ics20 implementation, open-sourced on GitHub since January 2023 , was adapted for Axelar by switching from an escrow model to one that mints wrapped tokens on receipt, a change that required removing two functions that only made sense in the original architecture. 

 Vulnerable Contract: 
 secret1yxjmepvyl2c25vnt53cr2dpn8amknwausxee83 

 The first removed function, parse_voucher_denom(&msg.denom, &packet.src) , would have validated that the incoming token's denomination path matched the actual source channel of the packet.

 The second, reduce_channel_balance(...) , would have capped minting to the amount that channel had genuinely deposited.

 Both were gone. What replaced them was an allow-list : If the token name appeared on the approved list, the contract minted.

 Yi traced it precisely in a fourteen-part thread on June 19th : "The contract asks 'is this denom supported?' It does not ask 'is this packet authorized?'" 

 Because opening an IBC channel is permissionless by design , the attacker needed nothing else. 

 The attacker forged deposits from a counterfeit chain , opened a fresh IBC channel to the Secret-side contract, and sent packets carrying the approved token denominations.

 The contract asked only whether the denom was supported , not whether the packet was authorized.

 The bug traces back to the repository's initial commit on January 15, 2023 . It deployed to mainnet on March 30, 2023 .

 A routine migration on March 5, 2026 , updated the bytecode for new features and carried the same missing checks forward, untouched. 

 No independent audit was commissioned for the fork . 

 Three years, one integration and it appears that no one even bothered to look.

 Rarma put it without ceremony : "Secret Network let a couple of commented lines drain their Axelar-bridged TVL for $4.67M. It's been in their open-source repo since 2023."

 For three years the contract asked only whether a denom was allowed, not whether the packet was authorized. 

 So who, exactly, was reading? 

## Permissionless Drain

 The attacker spent most of June 10th on preparation. 

 Between 06:50 and 18:54 UTC they created light clients , opened test channels, moved small amounts of native funds, and probed the exit route. 

 Twelve hours of reconnaissance against a contract that had been sitting in plain sight for three years.

 At 19:01 UTC they created the live client for their fake chain , ID ibc-dev-allowlist-denom-1.

 By 19:05 they had opened channel-227 directly to the bridge contract.

 At 19:14 the first forged packet landed , at 19:20 the last one cleared .

 Seven tokens, each minted to the current total locked value of its saToken , with nothing backing them, in six minutes. 

 Between 19:33 and 19:36 UTC the attacker pushed all seven unbacked saTokens back through channel-61 to Axelar, and Axelar's channel-69 escrow account unlocked the equivalent amount of real assets automatically. 

 Axelar's escrow released real assets automatically. Secret Network’s Security Incident Report describes no alert, pause, or circuit-breaker response during this phase. From there, 18 IBC transfers in three batches between 19:38 and 19:56 UTC moved everything through Osmosis via packet-forwarding , then bridged to Ethereum and consolidated into approximately 2,350 ETH on CoW Protocol between 20:04 and 20:15 UTC .

 Thirty transfers of 50 to 139 ETH followed across the next thirteen hours , each going to a fresh wallet, all forwarding onward. 

 The attacker added fake ERC-20 tokens with Unicode symbols mimicking ETH and BNB to clutter the trail , a cosmetic move that added noise without hiding much. 

 Attacker's Ethereum Wallet: 
 0x6c2eAB82bA2897A6E99FB6Af018020dA15123976 

 The proceeds resolved to three exchanges : KuCoin, ChangeNow, and HitBTC.

 KuCoin received approximately 1,199 ETH , a KYC exchange with subpoena-able records.

 ChangeNow received approximately 1,050 ETH , a non-KYC instant swap where funds convert and vanish.

 HitBTC received approximately 100 ETH . 

 Roughly 170 ETH remained unattributed . 

 KuCoin Hot Wallet: 
 0x45300136662dd4e58fc0df61e6290dffd992b785 

 ChangeNow Wallet: 
 0xeba88149813bec1cccccfdb0dacefaaa5de94cb1 

 HitBTC Wallet: 
 0x80787af194c33b74a811f5e5c549316269d7ee1a 

 CoW Protocol Settlement Contract: 
 0x9008d19f58aabd9ed0d60971565aa8510560ab41 

 Attacker's Secret Wallet: 
 secret154pdez8zazqh26wyuyu70nqraal3hkvf2f03vm 

 Attacker's Axelar Wallet: 
 axelar1hzra9z4zn8q0w8f3dj2wnw0xgetu8dfdhl6ad8 

 Attacker's Osmosis Wallet: 
 Osmo1hzra9z4zn8q0w8f3dj2wnw0xgetu8dfdm2l9s5 

 Roughly $642K remains in the attacker's Axelar wallet , holding 6.2 WBTC, 239,324 USDC, 64.04 WBNB, and 248.85 AXL.

 The trail is documented. The funds are mostly gone. And that $642K is sitting in a wallet Secret Network asked Axelar to freeze, a request Axelar did not pursue . 

 So what exactly does "coordinating with law enforcement" mean when the money is still right there? 

## Finger Pointing

 Both teams published statements on June 19th. 

 Both were accurate. Neither was sufficient. 

 Axelar was direct : "Neither Axelar nor IBC was compromised. The exploited token smart contract was not developed, deployed, or maintained by Axelar."

 Their post continued : “This deployment was vulnerable because its Secret-side fork had core security checks removed. The issue was not Axelar-specific logic or a flaw in IBC itself.”

 Secret Network aimed at a different failure : The contract had a bug, yes. But when forged tokens were redeemed through the legitimate channel, Axelar's channel-69 escrow account unlocked the equivalent real assets automatically , with nothing flagging it.

 Secret Network : "No effective monitoring, anomaly-detection, or emergency pause mechanisms were triggered within the Axelar bridge infrastructure to identify and temporarily halt unusually large or suspicious transfers before the bridge assets were substantially drained from Axelar." 

 The quietest line in Secret's post carried the most weight : “No external audit was requested by Axelar as part of the integration.”

 The Axelar-Secret integration was announced on July 13, 2022 . The fork shipped to Secret Network in March 2023 . 

 Because no external audit was requested by Axelar as part of the integration , the custom code that changed how the contract trusted its counterparties appears to have gone unreviewed for three years.

 Common Prefix authored the exploit report . It named both failures without flinching.

 About $642K remains in the attacker's Axelar wallet .

 Secret Network asked Axelar to freeze it, a request Axelar decided not to pursue .

 Axelar said it is coordinating with exchanges and law enforcement .

 The Secret and Secret-SNIP connections remain disabled with no timeline given . 

 When a custom integration changes the trust model and nobody commissions a new audit, who owns the failure when the bridge empties? 

 This was not a sophisticated attack. It was a patient one. 

 Ray Raspberry identified five Cosmos ecosystem chains drained in 35 days , roughly $21M gone. 

 Gravity Bridge lost $5.4 million in late May , after a patch had sat unread on GitHub for 123 days before the exploit ran .

 Namada was drained for $600K , and the loss stayed invisible until someone checked live RPC against a stale indexer .

 The pattern across all of them is not a single bug class. It's an operational condition: Real money parked in infrastructure that the people who built it have largely moved on from, watched by nobody, audited by nobody.

 Ray Raspberry called it plainly : "The attacker's innovation isn't technical. It's reading the room. Ghost chains still hold real money." 

 The door on this contract had been open for three years, public, requiring nothing more than someone willing to look.

 Someone looked. They came back with a fake chain, a fresh IBC channel, and eighteen minutes to spare. 

 If real money keeps sitting in infrastructure that nobody is actively watching, what exactly is the working theory for how it stays safe? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
