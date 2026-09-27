# [H] MEV Bots incident: A bot named 0xbadc0de made a windfall when traders tried to sell 1.8 million cUSDC (USDC on the Compound protocol) ($1.85 million

## Summary
Severity: High
Target: MEV Bots
Loss: $ 1,500,000
Attack method: Contract Vulnerability
Published: 2022-09-28
Source: https://rekt.news/ripmevbot/
Type: slowmist-incident

## Details
A bot named 0xbadc0de made a windfall when traders tried to sell 1.8 million cUSDC (USDC on the Compound protocol) ($1.85 million in nominal value), but only got $500 of the asset due to low liquidity in return. However, the MEV bot made a profit of 800 ETH (~$1 million) from the sold carry trade. An hour later, a hacker exploited a bug in 0xbadc0de's badc code to withdraw all 1,101 ETH (~$1.5 million) in the contract.
