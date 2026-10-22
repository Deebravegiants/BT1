# [H] Non-Governance-Based Admin of TimeLock And Related Privileges

## Summary
Severity: High
Contest weight: 0.3834
Dataset id: 13117
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In SushiSwap, the governance contract, i.e., GovernorAlpha, plays a critical role in governing and regulating the system-wide operations (e.g., pool addition, reward adjustment, and migrator setting). It also has the privilege to control or govern the life-cycle of proposals and enact on them regarding their submissions, executions, and revocations. With great privilege comes great responsibility. Our analysis shows that the governance contract is indeed privileged, but it currently has NOT been deployed yet to govern the MasterChef contract that is the central to SushiSwap. In the following, we examine the current state of privilege assignment in SushiSwap. Specifically, we kept track of the current deployment of various contracts in SushiSwap and the results are shown in Table 3.1.

Table 3.1: Current Contract Deployment of SushiSwap
Contract
Address
Owner/Admin
SUSHIToken
0x6b3595068778dd592e39a122f4f5a5cf09c90fe2
0xc2edad668740f1aa35e4d8f227fb8e17dca888cd
MasterChef
0xc2edad668740f1aa35e4d8f227fb8e17dca888cd
0x9a8541ddf3a932a9a922b607e9cf7301f1d47bd1
Timelock
0x9a8541ddf3a932a9a922b607e9cf7301f1d47bd1
0xf942dba4159cb61f8ad88ca4a83f5204e8f4a6bd
Deployer/DevAddr
0xf942dba4159cb61f8ad88ca4a83f5204e8f4a6bd
Migrator
0x0000000000000000000000000000000000000000
Confidential

To further elaborate, we draw the admin chain based on the current deployment of SushiSwap in Figure 3.2. We emphasize that the SUSHI token contract is properly administrated by the MasterChef contract that is authorized to mint new SUSHI tokens per block. The MasterChef contract is administrated by the Timelock contract and this administration is also appropriate as the Timelock contract is indeed authorized to configure various aspects of MasterChef, including the addition of new pools, the share adjustment of each existing pool (if necessary), and the setting of the upcoming migrator contract.

Figure 3.2: The Current Admin Chain of SushiSwap

However, it is worrisome that Timelock is not governed by the GovernorAlpha governance contract. Our analysis shows that the current Timelock control is controlled by an externally-owned account (EOA) address, i.e., 0xf942dba4159cb61f8ad88ca4a83f5204e8f4a6bd. This EOA address happens to be the same deployer address of SushiSwap and also configured as the development team address, i.e., devaddr. With a proper community-based on-chain governance, its admin chain should be depicted as follows:

Figure 3.3: The Expected Admin Chain of SushiSwap

In the meantime, we notice the GovernorAlpha contract has a special guardian that has certain privilege, including the cancellation of ongoing proposals that has not been executed yet. However, since this contract has not been deployed and this part of logic is directly borrowed from Compound without any modification, we do not expand further.1

1Interested readers are referred to the original GovernorAlpha audit report conducted by OpenZeppelin and the Confidential

## Recommendation
Promptly transfer the admin privilege of Timelock to the intended GovernorAlpha governance contract. And activate the normal on-chain community-based governance life-cycle and ensure the intended trustless nature and high-quality distributed governance.
