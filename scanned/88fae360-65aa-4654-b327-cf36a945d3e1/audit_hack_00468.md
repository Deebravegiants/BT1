# [H] Purrlend incident: According to Purrlend's official post-mortem report, Purrlend suffered a security incident on April 25. The deployments on HyperEV

## Summary
Severity: High
Target: Purrlend
Loss: $ 1,520,000
Attack method: Admin Privilege Abuse
Published: 2026-04-25
Source: https://x.com/purrlend/status/2049807764944458094?s=46
Type: slowmist-incident

## Details
According to Purrlend's official post-mortem report, Purrlend suffered a security incident on April 25. The deployments on HyperEVM and MegaETH incurred a total loss of approximately $1.52 million. The attacker compromised the team's 2/3-admin multi-signature wallet, granting malicious addresses various administrative permissions, including the BRIDGE_ROLE. Subsequently, the attacker used the mintUnbacked function to mint approximately 2 million unbacked pUSDm and 4.85 million pUSDC without collateral. These tokens were then used as collateral to borrow real assets from the liquidity pools. HyperEVM suffered a loss of about $1.2 million, while MegaETH lost approximately $325,000. Purrlend has paused the protocol, revoked the permissions, and contacted law enforcement agencies as well as blockchain analytics firms to trace the funds. The root cause of the incident was the lack of a time-lock in the multi-signature configuration, rather than any vulnerability in the smart contract logic itself. The team is currently exploring compensation options.
