# [H] USPD incident: According to PeckShieldAlert, the stablecoin project USPD has suffered a major security breach, resulting in approximately $1 mill

## Summary
Severity: High
Target: USPD
Loss: $ 1,000,000
Attack method: "CPIMP" (Clandestine Proxy In the Middle of Proxy) attack
Published: 2025-12-04
Source: https://x.com/PeckShieldAlert/status/1996826080741937213
Type: slowmist-incident

## Details
According to PeckShieldAlert, the stablecoin project USPD has suffered a major security breach, resulting in approximately $1 million in losses. The USPD team later confirmed that the protocol had been exploited, with the attacker minting tokens without authorization and draining liquidity. The official team has urgently advised users to revoke all token approvals granted to the USPD contract. According to the project’s confirmation, the incident was identified as a “CPIMP” attack. During the deployment phase, the attacker used Multicall3 to preemptively initialize the proxy and seize administrator privileges, while disguising the malicious implementation as an audited contract. The hidden logic remained dormant for several months before being activated, allowing the attacker to upgrade the proxy, mint approximately 98 million USPD tokens, and transfer around 232 stETH. The USPD team has disclosed the attacker addresses (Infector: 0x7C97…9d83, Drainer: 0x0833…215A) and stated that they are working with law enforcement and white-hat partners to trace the funds. The team has also offered a 10% bounty if the attacker returns the stolen assets.
