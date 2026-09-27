# [H] Third-party Gnosis Safe Module (SquidRouterModule) incident: A third-party Gnosis Safe module named SquidRouterModule was exploited, draining approximately $3-3.2 million from 86 Gnosis Safe

## Summary
Severity: High
Target: Third-party Gnosis Safe Module (SquidRouterModule)
Loss: $ 3,200,000
Attack method: Smart Contract Vulnerability
Published: 2026-05-25
Source: https://x.com/squidrouter/status/2058890710611276238
Type: slowmist-incident

## Details
A third-party Gnosis Safe module named SquidRouterModule was exploited, draining approximately $3-3.2 million from 86 Gnosis Safe wallets on Ethereum and Base within about 2 hours. The module has no affiliation with the official Squid Router protocol—confusion arose solely due to the contract name on Basescan. Victims had previously added this faulty third-party module as a trusted Safe Module, granting it permission to spend any tokens without signatures. The attacker exploited weak authentication (accepting a publicly visible constant string as "message security" proof) to execute arbitrary calldata, forcing fake Uniswap V3 swaps (real tokens for worthless 'u' token in attacker-controlled pools) and draining funds, which were consolidated into ~3.07M DAI. Squid confirmed its core router and user funds/integrations remain fully secure.
