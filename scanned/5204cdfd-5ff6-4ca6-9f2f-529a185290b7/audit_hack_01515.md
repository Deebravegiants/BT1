# [H] Value DeFi incident: Value DeFi stated that at 11:22 on May 5th, the attacker reinitialized the fund pool and set the operator role to himself, and _st

## Summary
Severity: High
Target: Value DeFi
Loss: $ 5,817,780
Attack method: Contract Vulnerability
Published: 2021-05-05
Source: https://medium.com/valuedefi/vstake-pool-incident-post-mortem-4550407c9714
Type: slowmist-incident

## Details
Value DeFi stated that at 11:22 on May 5th, the attacker reinitialized the fund pool and set the operator role to himself, and _stakeToken was set to HACKEDMONEY. The attacker controlled the pool and called governmentRecoverUnsupported (), which was exhausted. The original pledge token (vBWAP/BUSD LP). Then, the attacker removes 10839.16 vBWAP/BUSD LP and liquidity, and obtains 7342.75 vBSWAP and 205659.22 BUSD. Subsequently, the attacker sells all 7342.75 vBSWAP at 1inch to obtain 8790.77 BNB, and buys BNB and BUSD renBTC through renBridge. Converted to BTC. The attacker made a total of 205,659.22 BUSD and 8,790.77 BNB. The 2802.75 vBSWAP currently in the reserve fund and the 205,659.22 BUSD of the ValueDeFi deployer will be used to compensate all users in the pool. The remaining 4540 vBSWAP can be compensated in the following two ways. The first option is to cast 4540 vBSWAP to immediately compensate all affected users, and the other option is to cast 2270 vBSWAP to immediately compensate, and the rest will be returned to the contract within 3 months. Value DeFi emphasized that only the vStake profit sharing pool of vBSWAP in bsc.valuedefi.io has received the impression, and other fund pools and funds are in a safe state.
