# [M] Goose Finance incident: Goose Finance, a yield farming protocol on BNB Chain, was exploited due to a share accounting flaw in the StrategyGooseEgg contrac

## Summary
Severity: Medium
Target: Goose Finance
Loss: $ 8,435
Attack method: Smart Contract Vulnerability
Published: 2026-03-14
Source: https://blocksec.com/blog/weekly-web3-security-incident-roundup-mar-9-mar-15-2026
Type: slowmist-incident

## Details
Goose Finance, a yield farming protocol on BNB Chain, was exploited due to a share accounting flaw in the StrategyGooseEgg contract. The attacker repeatedly looped deposit() and withdraw() to mint inflated shares before rewards were settled, then redeemed them at higher value after harvest, profiting ~$8,435.
