# [M] CL-2021-38: API token can be read from a log file by any user

## Summary
Severity: Medium
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2021-12-01
Source: https://github.com/sigp/lighthouse/issues/2438
Type: ef-disclosure

## Details
Affected Clients: Lighthouse
Uid: CL-2021-38
Bug: API token can be read from a log file by any user
Type: BUG
Summary: A validator client uses two API keys: ".secp-sk" (secret key) and "api-token.txt" (the corresponding public key).<br>The spec suggests that an API token can be obtained (read) from a file or from logs.<br><br>The second method is highly insecure by design and considered as a very bad practice in web application security (e.g., OWASP Logging).<br><br>Moreover, an API token can be read from the log file by any user on the host because the file permissions for the logs are 644.
Links: [https://github.com/sigp/lighthouse/issues/2438](https://github.com/sigp/lighthouse/issues/2438)
Reported: 2021-07-07
Fixed Date: 2021-09-13
Published: 2021-12-01
Severity: Medium
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11684
Bounty Reward (Usd): 0
