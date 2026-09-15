# [M] YAM incident: On August 13, 2020, the well-known Ethereum DeFi project YAM officially issued a post on Twitter indicating that there were loopho

## Summary
Severity: Medium
Target: YAM
Loss: $ 750,000
Attack method: Contract Vulnerability
Published: 2020-08-13
Source: https://medium.com/yam-finance/yam-post-rescue-attempt-update-c9c90c05953f
Type: slowmist-incident

## Details
On August 13, 2020, the well-known Ethereum DeFi project YAM officially issued a post on Twitter indicating that there were loopholes in the contract. The price plummeted by 99% within 24 hours, resulting in the “permanent destruction” of the governance contract, with a value of 750,000 USD Curve tokens. It is locked and cannot be used. Since the value of totalSupply was taken during rebase, the value of totalSupply calculated incorrectly will not be immediately applied to initSupply through mint, so before the next rebase, the community still has a chance to recover this error and reduce losses. But once the next rebase is executed, the entire mistake will become irreparable.
