# [H] Loopscale exploit: Fresh off their launch party, the Solana lending protocol watched helplessly as an attacker drained $5.8 million through their gaping oracle vulnerabi

## Summary
Severity: High
Target: Loopscale
Loss: $5,800,000
Published: 4/26/2025
Source: https://rekt.news/loopscale-rekt
Type: rekt-postmortem

## Details
## Loopscale - Rekt

 Thursday, May 1, 2025 Loopscale - Rekt - Oracle Manipulation 

 read this article also in : 

 Sixteen days. That's all it took for Loopscale to join crypto's hall of shame. 

 Fresh off their launch party, the Solana lending protocol watched helplessly as an attacker drained $5.8 million through their gaping oracle vulnerability on April 26. 

 One stale price feed was all it took - the digital equivalent of leaving your vault combination taped to the front door. With an audit report warning about oracle validation issues, Loopscale's team somehow found time to market but apparently not time to patch.

 Their attacker didn't need a PhD in blockchain vulnerabilities - just a basic playbook: mess with collateral prices, grab under-collateralized loans, empty the vaults, bridge the loot, and vanish into crypto's shadowy corners.

 Now Loopscale joins crypto's endless conga line of hacked protocols - sliding into their attacker's DMs with bounty offers while tweeting reassurances like a pilot smiling through engine failure. 

 When will protocols learn that flashy launches mean nothing if your security is held together with digital duct tape? 

 Credit: Loopscale , Mary Gooneratne , Max N. , Sean Hu , Bill Papas , Phat Bear 
 Stale prices and undercollateralized loans - a match made in DeFi hell. 

 Loopscale slammed the brakes on their markets and announced the exploit - but by then, the vaults were already bleeding out.

 Mary Gooneratne, Loopscale's co-founder chimed in , "an attacker took out a series of undercollateralized loans on the protocol, exploiting the Loopscale USDC and SOL Vaults for ~$5.8M."

 The exploit's surgical precision would be impressive if it weren't so damn predictable.

 While Loopscale scrambled to contain the situation, Max N. had already spotted the smoking gun - the attacker simply deployed a malicious price feed and called Loopscale's own create_loan function, elegantly sidestepping security measures with the digital equivalent of a counterfeit ID. 

 How many times must this lesson be learned? 

 Price oracle manipulation has been one of DeFi’s oldest tricks in the book - and somehow, protocols still keep leaving the back door wide open.

 The attack stripped roughly 12% of Loopscale's total value in minutes, exploiting a pricing flaw that Loopscale later admitted was an isolated issue with how they handled RateX-based collateral in their newly launched SOL and USDC Genesis vaults.

 RateX's founder Sean Hu wasted no time distancing his protocol from the carnage: "Based on our investigation, the Loopscale incident has been confirmed as an oracle attack. RateX's protocol itself has no security issues." Translation: don't blame our price feed - blame the idiots who implemented it.

 But the truly impressive part? The attacker didn't need to hack Loopscale's code - they simply reverse-engineered it from the binary. 

 In the digital world, obscurity isn't security.

 As Twitter user Bill Papas explained , the attacker could extract Loopscale's Interface Description Language from the deployed binary, then analyze transaction patterns to recreate functionality locally - essentially reading the lock's blueprint while everyone thought it was safely hidden.

 Closed source doesn't mean secure. It just means your vulnerabilities are hidden until they're catastrophically exploited. 

 But when a protocol gets dissected this easily, one has to wonder - was this just lazy security, or something more convenient? 

## Following the Money

 The attack took place on Solana, then the funds were bridged to Ethereum through Wormhole. 

 Loopscale Exploiter 1 (Used to move funds to Ethereum): 

 4QsqugQcrCuSVzU9WjeLDoR6HaaSZtMEZr5JCyxwHgCV 

 Loopscale Exploiter 2 (Used to exploit protocol on Solana): 

 C1QyPYoWQiueqhtLeaG5Nhkv1LJ8oweBNCbfGJ3LprYT 

 Theft activity by Loopscale Exploiter 2 on Solana. 

 Attack Transaction 1 ($1.5 million USDC): 

 https://solscan.io/tx/2Cti6x4wMw2CCvDwQYa4JvnHZAeQaSu6krAtMnBjx9mxHpr3LTmbRDwZs21fjRiwU2Z5dV4BTJbkjaD7E2mxrRrq 

 Attack Transaction 2 ($1.5 million USDC): 

 https://solscan.io/tx/55dmSjy4Whjfqbfp8LwRduzTwz1fDeLu6aj8STqDXeiezZneNJwr2XiX3Qy7yWb2G2DL3d991ACD6sejNkQ7eH5Q 

 Attack Transaction 3 ($1.5 million USDC): 

 https://solscan.io/tx/XxksDRzx1KFVJpUzVCFDjRCXJcUzwbdTRYPmHQzZwmzYS6DptV8qAJxU2CGAXhxyPvWLPitFCAuPA6ASBG5beub 

 Attack Transaction 4 ($1.226.7 million USDC): 
 https://solscan.io/tx/2SkCkmX2Q8R7W7RDzgfc6ZFCmYgehmENw72sgTQLfNLHGupNdPDeNkW6S7qCNgYtintFcxhkBCsyf81XA9NSF2RJ 

 With the loot secured, the attacker swiftly converted USDC to SOL before making their cross-chain journey. 

 Swapped USDC for SOL: 
 https://solscan.io/tx/bR4YweLndnAAUX3DxwSfSqQNZcTgjdhnamLg35hF7tKzMnTPEzHvyAyQJtsAooKwgXY68tBuZzptc2R4aCqLz7H 

 Transfer stolen funds from Loopscale Exploiter Address 2 to Loopscale Exploiter Address 1 ($5.792 million in SOL - 39474.5 SOL): 

 https://solscan.io/tx/4uG4fVWmxXuZXNxw2BLWfTFVFbU4aYoqJ6PTntcD2dvRG9wL8csJraZ1MXYK8HjLWp5Wc6k3bwSfgcK861KTigN7 

 Loopscale Exploiter 1 transferred the funds through Wormhole in 3 transactions. 

 Wormhole Transaction 1 (5000 SOL - $735k): 
 https://solscan.io/tx/4KHQphm8CSS9YxgDiKgAfsLmTceFLYD8f9JEiaoZZRi7RQxfL3kPY4MD9GXuazeG6eyebChuupkQBA93ufh41QU2 

 Wormhole Transaction 2 (10000 SOL - $1.47M): 
 https://solscan.io/tx/FcafMbKHC4e1bArfsWJTDDgYtqktWTLeptmBnpGpSKZTdkSFYUJqtffwmvV1PQTX7Vfxp1EjHdjWMFcw1VWahTH 

 Wormhole Transaction 3 (20000 SOL - $2.96 million): 
 https://solscan.io/tx/5XzyPcvEL8JRD4B8rZcQxKCAi3FtxFYmGBjaWw5rSAu3ET3Z59RHuJafSJebeazZ3xDZDj9Qum8EubRchzN1Gm1e 

 Meanwhile on Ethereum… most of the stolen funds have been returned after the negotiation. 

 Stolen Funds Returned Transaction 1 ($737k): 
 0x4a5772b6249e080235c473558559156a3c97017f7af6be6aff0d5a95b5dc72f0 

 Stolen Funds Returned Transaction 2 ($1.47 million): 
 0x17f799be2c200473822afd8175fc1adc281ab361d50d98ebf9e2fd08555595ce 

 Stolen Funds Returned Transaction 3 ($2.96 million): 
 0xa92ff591cad42bd2886ef5040e702c8540ed7c302d7b507dbf237d0353407860 

 Back on Solana, Loopscale Exploiter 1 transferred 4,464 SOL ($664k) back to Loopscale: 
 66YqTDPxYukrPtwfPbXv3utHKi2KfqvXXf3De3Km5eQ9GjSbY2kYe1yBk4zVj371fH8BjT9CCPqv4w4wQXnRaxei 

 With every coin accounted for, the money trail ended — but the real drama was just beginning.

 What does it say about DeFi security when the ransom notes are part of the incident response plan? 

## The Negotiation and Aftermath

 Loopscale's post-exploit playbook hit all the classics. 

 First came the damage control. Markets halted. Users reassured. Bridges and exchanges are notified. 

 The protocol even managed to re-enable loan repayments and loop closing within hours - though vault withdrawals remain locked while they "investigate."

 Then, the inevitable ransom note. Like desperate parents trying to negotiate with a kidnapper.

 Loopscale sent their exploiter the crypto equivalent of a handwritten plea: 

 "We are aware that you exploited a vulnerability in Loopscale's pricing system earlier today... We'd like to offer you a whitehat agreement in exchange for returning 90% of the exploited funds (35,527 SOL)... we agree to allow you to retain a bounty of 10% of the funds (3,947 SOL) and release you from any and all liability." 

 The dramatic 24 hour countdown clock was included, but the exploiter wasn't buying the standard 10% offer.

 Their counter-proposal arrived with characteristic audacity:

 "We are agreeable to collaborating with you to reach a white hat agreement. However, we would like to negotiate the bounty percentage; our expectation is 20%."

 To demonstrate their "good faith," they immediately returned the 5,000 SOL ($735k) bridged in their first transaction. 

 A clever psychological play - return the smallest portion while holding the remaining millions hostage. 

 The attacker made it clear that the 20,000 SOL in Wormhole’s limbo was no longer their responsibility, leaving Loopscale to navigate the next steps with the bridge themselves.

 By Sunday morning, after negotiations began, the first two bridged amounts mysteriously found their way back to Loopscale - $2.2 million returned while $2.96 million sat in bridge limbo.

 Finally on early Tuesday morning, the exploiter sent back the previously frozen 20,000 SOL ($2.96 million), putting an end to the caper.

 By April 29, Loopscale confirmed that all stolen funds had been returned - a rare happy ending in DeFi's exploit theater.

 Following the successful negotiations, Loopscale assured that “Users will incur no loss of deposits from this incident. Additional details (including information on vault withdrawals) to follow.” 

 While the team publicly offered a 10% bounty during negotiations, they remain suspiciously silent about whether the exploiter will receive compensation for returning the loot, even when Rekt News reached out, they’re keeping it under wraps for now. 

 All's well that ends well? Not quite.

 Just because a heist ends with returned funds doesn't mean the vault was ever secure.

 One Twitter user, Phat Bear, said the quiet part out loud : "While Loopscale was transparent about the issue, this was still a severe exploit. You guys opened the Genesis vaults with very high cap ($40M total), but did not conduct a thorough audit on them first."

 The $40 million in Genesis vaults wasn't an oversight - it was a deliberate threshold set by a protocol that had just emerged from beta, apparently confident their security was bulletproof despite warnings in their audit.

 OShield's audit warned about oracle validation, but also reported that it was fixed . 

 When your protocol claims 'all critical issues fixed' while leaving the door wide open, is it incompetence or hubris that's really to blame? 

 Sixteen days post-launch, Loopscale learned the most expensive lesson in DeFi: audits aren't suggestions, they're survival manuals. 

 Despite recovering all user funds, the reputational damage can't be so easily patched with a GitHub commit. 

 But time will tell, as their response to the hack and successful negotiations may be their saving grace.

 No amount of promised transparency or future post-mortems can erase the fact that they launched a protocol holding millions in user funds while their oracle validation was as robust as a paper umbrella in a hurricane.

 The protocol's security architecture crumbled against an attack vector older than most NFT collections.

 The bitter irony? Documentation claimed "all critical and high-risk issues identified have been fixed" right before an attacker casually exploited the exact vulnerability type their audit had flagged. 

 Will protocols ever realize that ignoring security risks today is setting the stage for their own downfall tomorrow? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
