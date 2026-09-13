# [H] Dango incident: The DeFi project Dango released an update three hours after disclosing a security incident last night, stating that the white-hat

## Summary
Severity: High
Target: Dango
Loss: $ 1,900,000
Attack method: Insurance Fund Logic Vulnerability
Published: 2026-04-13
Source: https://x.com/dango/status/2043710283244331409
Type: slowmist-incident

## Details
The DeFi project Dango released an update three hours after disclosing a security incident last night, stating that the white-hat hacker has fully returned the stolen funds and received a bug bounty. User funds were not affected. The founder of Dango said that fixes will be deployed, additional security measures will be implemented, and preparations are underway to restart the blockchain. According to the earlier announcement, the attacker exploited a logic flaw in the insurance fund to steal USDC collateral. The vulnerability arose because the insurance fund allowed anyone to make donations but failed to verify that the donation amount was positive. Thanks to rate limits on the cross-chain bridge, the attacker was only able to bridge $410,000 worth of USDC to Ethereum, while the remaining $1.49 million stayed on Dango and was successfully recovered. The vulnerability has now been fixed and does not affect other trading system functions such as order matching, PnL settlement, or liquidation.
