# [M] Solido Cash incident: Solido Cash (the largest DeFi protocol on Supra) was exploited due to an oracle misassignment on SOLID collateral (stale feed fall

## Summary
Severity: Medium
Target: Solido Cash
Loss: $ 73,400
Attack method: Oracle Misassignment
Published: 2026-07-23
Source: https://x.com/SolidoMoney/status/2081323242854469730
Type: slowmist-incident

## Details
Solido Cash (the largest DeFi protocol on Supra) was exploited due to an oracle misassignment on SOLID collateral (stale feed fallback to CASH oracle, severely overvaluing collateral). The attacker, in two waves (one atomic tx + one multi-wallet manual), deposited cheap collateral, minted excess CASH, and sold it on DEXs for SUPRA, netting ~293.7M SUPRA. No user funds were affected; losses primarily hit LPs (mostly the foundation) and protocol reserves. The protocol paused relevant functions and released a forensic report.
