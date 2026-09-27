# [H] MEV Bot incident: The MEV bot operated by JaredFromSubway.eth was drained of approximately $7.5 million. Attackers deployed fake token wrappers and

## Summary
Severity: High
Target: MEV Bot
Loss: $ 7,500,000
Attack method: Business Logic Flaw
Published: 2026-06-20
Source: https://x.com/PeckShieldAlert/status/2068457314416545978
Type: slowmist-incident

## Details
The MEV bot operated by JaredFromSubway.eth was drained of approximately $7.5 million. Attackers deployed fake token wrappers and liquidity pools to trick the bot’s automated MEV execution system into granting token approvals to attacker-controlled contracts. They then exploited the unrevoked approvals to transfer out WETH, USDC, and USDT via transferFrom. It was not a traditional phishing attack or a vulnerability in the victim contracts themselves, but a flaw in the bot’s automated approval-generation mechanism. Jared publicly offered a $1 million bounty for full recovery with full confidentiality.
