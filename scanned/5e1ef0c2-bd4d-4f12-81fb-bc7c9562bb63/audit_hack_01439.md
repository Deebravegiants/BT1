# [M] OpenZeppelin incident: OpenZeppelin released a bug fix analysis. Whitehat Zb3 submitted a serious reentrant vulnerability in OpenZeppelin's TimelockContr

## Summary
Severity: Medium
Target: OpenZeppelin
Loss: -
Attack method: Contract Vulnerability
Published: 2021-09-03
Source: https://forum.openzeppelin.com/t/timelockcontroller-vulnerability-post-mortem/14958
Type: slowmist-incident

## Details
OpenZeppelin released a bug fix analysis. Whitehat Zb3 submitted a serious reentrant vulnerability in OpenZeppelin's TimelockController contract on August 21, 2021, which affected a project hosted on the Immunefi vulnerability bounty platform. The project chose to remain anonymous and has paid an undisclosed amount (including an anonymous bonus) to White Hat. OpenZeppelin paid White Hat a bonus of $25,000 to recognize their contribution to community security and released a patch. As far as it knows, this is the only serious vulnerability that OpenZeppelin has in its open source smart contract library. The vulnerability has been patched in the affected projects, and OpenZeppelin has released an updated contract version to fix the vulnerability. All projects that use TimelockController should be migrated.
