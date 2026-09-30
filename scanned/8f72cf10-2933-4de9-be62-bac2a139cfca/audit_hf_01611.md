# [H] H-2 Centralization Risks and Market Maker Potential Exploits

## Summary
Severity: High
Contest weight: 0.2704
Dataset id: 8647
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This issue has been identified regarding the protocol's upgradeability and the market maker's control over user funds.
Admin Centralization: As the contract is upgradeable, the admin can modify core protocol logic at any time. If a single, potentially compromised individual or entity controls this role, they could introduce malicious code or alter system parameters without user consent, leading to a total takeover of user funds.
Market Maker Privilege: The market maker can execute trades on its own LOB positions, potentially at rates harmful to liquidity providers. For instance, a 1%-below-market swap with an address under its control could drain a large portion of the pool's value if made repeatedly. This risk grows if the market maker is less trusted than the admin but still has considerable influence.
The issue is classified as high severity because either the admin or the market maker can perform actions that jeopardize all participant funds, up to an almost complete loss.

## Recommendation
We recommend:
1. Implementing a multisig with a timelock for critical administrative (upgrade) functions. This restricts any single party from pushing harmful updates immediately.
2. Introducing a safety deposit mechanism for the market maker. If the market maker's trades cause protocol losses, they are first covered by its deposit. If losses approach the deposit limit, further market maker actions should be blocked, and the deposit seized if necessary.
These measures reduce the risks of centralized exploitation and ensure the market maker is financially liable for damaging trades.
2.3 Medium
