# [H] Dexible incident: The DEX tool Dexible was suspected of being attacked and lost about $2 million. According to the analysis, there is a logical loop

## Summary
Severity: High
Target: Dexible
Loss: $ 2,000,000
Attack method: Contract Vulnerability
Published: 2023-02-17
Source: https://www.panewslab.com/zh/sqarticledetails/y4jol3pw.html
Type: slowmist-incident

## Details
The DEX tool Dexible was suspected of being attacked and lost about $2 million. According to the analysis, there is a logical loophole in the selfSwap function of the Dexible contract, which will call the fill function. This function has a call to the attacker's custom data, and the attacker constructs a transferfrom function in this data, and transfers other users (0x58f5f0684c381fcfc203d77b2bba468ebb29b098) address and its own attack address (0x684083f312ac50f538cc4b634d85a2feafaab77a), causing the tokens authorized by the user to the contract to be transferred by the attacker.
