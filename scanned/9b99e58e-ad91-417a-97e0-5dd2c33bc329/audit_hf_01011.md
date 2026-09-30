# [M] Silo is not compatible with Fee-on-transfer or rebasing tokens

## Summary
Severity: Medium
Contest weight: 0.1948
Dataset id: 3514
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the documentation there are certain conditions that need to be met for a token to be whitelisted:

Additional tokens may be added to the Deposit Whitelist via Beanstalk governance. In order for a token to be added to the Deposit Whitelist, Beanstalk requires:
The token address;
A function to calculate the Bean Denominated Value (BDV) of the token (see Section 14.2 of the whitepaper for complete formulas); and
The number of Stalk and Seeds per BDV received upon Deposit.

Thus if the community proposes any kind of Fee-on-Transfer or rebasing tokens like (PAXG or stETH) and the Beanstalk governance approves it, then the protocol needs to integrate them into the system. But as it is now the system is definitely not compatible with such tokens.

deposit, depositWithBDV, addDepositToAccount, removeDepositFromAccount and any other silo accounting related functions perform operations using inputed/recorded amounts. They don't query the existing balance of tokens before or after receiving/sending in order to properly account for tokens that shift balance when received (FoT) or shift balance over time (rebasing).

Likelyhood - low/medium - At the moment of writing lido has over 31% of the ETH staked which makes stETH a very popular token. There's a strong chance that stakeholder would want to have stETH inside the silo.

Impact - High - It simply won't work.

Overall severity is medium.

## Recommendation
Clearly state in the docs that weird tokens won't be implemented via Governance Vote or adjust the code to check the token.balanceOf() before and after doing any operation related to the silo.
