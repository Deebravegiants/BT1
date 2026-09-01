# [M] CL-2021-39: File permissions for validator client API keys are insecure

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2021-12-01
Source: https://github.com/sigp/lighthouse/issues/2437
Type: ef-disclosure

## Details
Affected Clients: Lighthouse
Uid: CL-2021-39
Bug: File permissions for validator client API keys are insecure
Type: BUG
Summary: A validator client uses two API keys: ".secp-sk" (secret key) and "api-token.txt" (the corresponding public key).<br>Both files are stored in a user directory with 644 permission bits.<br>So any user on the host can read them.
Links: [https://github.com/sigp/lighthouse/issues/2437](https://github.com/sigp/lighthouse/issues/2437)
Reported: 2021-07-07
Fixed Date: 2021-09-13
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
