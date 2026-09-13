# [H] MobiusDAO exploit: It started with 67 cents and ended like a punchline no one was ready for

## Summary
Severity: High
Target: MobiusDAO
Loss: $2,150,000
Published: 5/11/2025
Source: https://rekt.news/mobiusdao-rekt
Type: rekt-postmortem

## Details
## MobiusDAO - Rekt

 Tuesday, May 13, 2025 MobiusDAO - Rekt 

 read this article also in : 

 It started with 67 cents and ended like a punchline no one was ready for. 

 On May 11, MobiusDAO’s Mobius Token ( MBU ) became the latest DeFi project to implode not from a sophisticated attack, but from elementary school math. 

 An attacker deposited 0.001 BNB and minted 9.73 quadrillion MBU tokens – enough to drain $2.15 million in actual stablecoins.

 The bug? A decimal handling error that turned pennies into quadrillions.

 Double the decimals, double the fun. 

 Blockaid spotted the tragic comedy show in the early hours of May 11th. 

 By the time Cyvers confirmed the attack shortly after , the attacker was already dumping tokens until MBU's price flatlined .

 The funds took their usual vacation to Tornado Cash - 21 neat transfers of 100 BNB each.

 In a system built on "code is law," nobody bothered to check if the law could do basic arithmetic. 

 Is this the future of finance - or just a $2.15 million magic trick, where the rabbit was decimal error and the hat was smart contract code? 

 Credit: Blockaid , Cyvers , MobiusDAO , AstraSec , Quill Audits , Noveleader , CertiK 
 MobiusDAO launched on May 8 with little more than a token address, a bare bones website , and some fancy buzz speak of “Dimensional Integration” for DeFi and RWAs. 

 There appears to be no audit, possibly no open-source code , no docs and no team that can be vetted publicly. Just a Telegram group and a Twitter account tweeting about 10x pumps .

 By May 11, it was over, as an attacker exploited a fatal decimal handling bug in the minting function.

 MobiusDAO stayed silent for over 10 hours, then issued a surreal statement blaming the “BSC Byzantine consensus mechanism” and promising cooperation with global law enforcement. 

 According to Quill Audits' autopsy , the fatal flaw lived in the deposit function. 

 When users deposited WBNB, the contract called getBNBPriceInUSDT to calculate how many MBU tokens to mint.

 The exploit was embarrassingly simple: a double multiplication in the price calculation.

 Noveleader from Quill Audits summarized it best: "The contract performed an extra multiplier of 10**18 on the amount the attacker deposited, inflating the amount deposited though the deposited amount was only $0.67."

 How did the mathematics of madness unfold across BSC with predictable precision? 

 Standard protocol: Tornado Cash for privacy, then deployment. The attacker was methodical where Mobius was not. 

 Tornado Cash Funding: 0x491b6888843f260587e86efaa26b837c6a1c26d17442a526088bb2ec46ee828f 

 Attacker: 
 0xB32A53Af96F7735D47F4b76C525BD5Eb02B42600 

 Next came the magic trick. Deploy a contract to do the dirty work. 

 Attacker's Contract: 
 0x631adFF068D484Ce531Fb519Cda4042805521641 

 The victim contract stood ready, its decimal flaw waiting to make someone rich. 

 Victim Contract: 
 0x95e92B09b89cF31Fa9F1Eca4109A85F88EB08531 

 MBU Token Contract: 
 0x0dfb6ac3a8ea88d058be219066931db2bee9a581 

 One transaction. 0.001 BNB in, 9.73 quadrillion MBU out. 

 Exploit Transaction: 0x2a65254b41b42f39331a0bcc9f893518d6b106e80d9a476b8ca3816325f4a150 

 The attacker had quadrillions to dump. PancakeSwap swallowed them whole, dragging MBU’s price straight to zero.

 Exit strategy? The classic 21 Tornado Cash spin cycles , 100 BNB each. Washed clean, protocol left for dead. 

 Ready to take a peak behind the code for how this tragic comedy of errors unfolded? 

## The Math That Broke the Bank

 Quill Audits broke down the farce step by step. 

 When the attacker called the deposit function with 0.001 WBNB, the contract fetched BNB's price: ~$656, correctly formatted with 18 decimals. 

 As Quill put it : "The problem arises as the function returns the value in 18 decimals, the contract multiplies this value again by 10**18, minting an enormous amount of tokens."

 This wasn't a sophisticated zero-day or a complex reentrancy attack. It was elementary school math gone nuclear. The protocol quite literally couldn't count its own zeros.

 The result? 9,731,099,570,720,980.659843835099042677 MBU tokens materialized from a 67-cent deposit.

 Once the tokens existed, the rest was mechanical: dump into PancakeSwap pools, crash the price to dust, walk away with $2.15 million.

 The token that launched on May 8 died on May 11. 

 Days later, MobiusDAO's latest post-hack bizarre announcement read like fever dream economics. 

 They called the exploit a "system data anomaly" and promised to keep paying 0.5% compound interest twice daily on "pre-attack collateral data" - whatever that meant.

 They vowed to "intercept abnormal transactions in real time" and undergo "audits by multiple auditing companies" before relaunching.

 Now promising yields on phantom collateral while discovering the magic of multi-sig wallets.

 A protocol that couldn't catch an extra multiplication suddenly claimed it could "intercept abnormal transactions in real time." 

 When a protocol can't tell the difference between $656 and $656 quintillion, are we building the future of money or just very expensive calculators that can't calculate? 

 Three days from debut to detonation - all because someone multiplied when they shouldn't have. 

 According to Astrasec , the contract wasn't even public. 

 The preventable flaws read like a checklist of what not to do: no mint cap, no validation, no testing.

 Just raw logic - possibly unaudited - programmed by someone who forgot how decimals work.

 MobiusDAO died the way it lived: abstract, maybe unaudited, and alone on the chain. 

 No documentation, no security review, no problem - until someone deposited 67 cents and walked away with millions.

 The protocol that promised "Dimensional Integration for DeFi and RWAs" couldn't integrate basic multiplication.

 In the end, Mobius created exactly what DeFi didn't need: another cautionary tale where ambition exceeded arithmetic. 

 They sold you on “Dimensional Integration” - but did you get anything more than multiplication malpractice? 

## SUBSCRIBE NOW

 email address * 

 share this article

 REKT serves as a public platform for anonymous authors, we take no responsibility for the views or content hosted on REKT.

 donate (ETH / ERC20): 0x3C5c2F4bCeC51a36494682f91Dbc6cA7c63B514C 

 disclaimer : 

 REKT is not responsible or liable in any manner for any Content posted on our Website or in connection with our Services, whether posted or caused by ANON Author of our Website, or by REKT. Although we provide rules for Anon Author conduct and postings, we do not control and are not responsible for what Anon Author post, transmit or share on our Website or Services, and are not responsible for any offensive, inappropriate, obscene, unlawful or otherwise objectionable content you may encounter on our Website or Services. REKT is not responsible for the conduct, whether online or offline, of any user of our Website or Services.
