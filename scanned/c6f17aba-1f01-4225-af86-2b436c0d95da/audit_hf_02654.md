# [M] Possible Market Manipulation

## Summary
Severity: Medium
Contest weight: 0.2470
Dataset id: 14387
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Note: This review did not focus on any analysis of economic incentives or their viability. However, this potential issue was recognised. While long term economic incentives appear to encourage “good behaviour” from staking node operators and the DAO governance system, the testing team has identified some potential scenarios where a malicious node operator or a voting majority of the DAO could harm the platform for short-term gain. As part of the current trust model, malicious node operators cannot steal funds, but can cause their provided stake to be slashed. Similarly, the DAO has the ability to vote to upgrade code or increase fees such that all subsequent rewards are provided to DAO token holders (in the treasury).2 Although the DAO governers and node operators cannot directly benefit from this (node operators would quickly get deactivated, and future ETH submissions could be reduced), these actions can cause the market value of stETH to drop and increase distrust in the platform. As stETH is an ERC20-like token, it can potentially be integrated into a wide range of DeFi applications and platforms. Several markets and derivative products could allow users to “short” stETH, profiting off the fall in stETH valuation. Because this is an indirect method of profit, it can be difficult to distinguish malicious from negligent behaviour. Similarly, shortly before Eth2 withdrawal is introduced as part of Phase 1.5, dumping the stETH price could allow for cheap purchase of stETH to be burnt and exchanged for ETH. Declining future prospects (e.g. unrelated indications that participation in Lido will drop or stagnate) may also encourage this short-term behaviour.

## Recommendation
Be careful to advise DAO members to carefully consider potential consequences when adding new node operators, adjusting staking limits, or making DAO tokens available for purchase. In particular, try to evaluate and balance potential gains of a malicious entity against long-term financial incentives, reputational or legal costs, and other collateral. The potential gains from such behaviour can vary depending on the amount of stETH liquidity available in DeFi protocols. Also consider that the effect of a malicious node operator on the market may be exaggerated past their staking limit. For example, given appropriate publicity, a malicious operator slashing 10 validators may cause similar fear to one controlling 100.  
2 For this to occur, a voting majority of the DAO would need to agree on the changes, or delegate the MANAGE_FEE role.  
Lido Finance Security Assessment
