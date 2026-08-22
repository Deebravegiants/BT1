# [?] CL-2021-44: VC: requests may not contain Authorization header with API token

## Summary
Severity: Unknown
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2021-12-01
Source: https://github.com/sigp/lighthouse/issues/2512
Type: ef-disclosure

## Details
Affected Clients: Lighthouse
Uid: CL-2021-44
Bug: VC: requests may not contain Authorization header with API token
Type: BUG
Summary: According to the Validator Client API documentation, all requests (GET, POST, PATCH) must contain Authorization header with the token.<br><br>The current implementation only requires the API token in GET requests only, POST/PATCH requests will be processed even if they don't contain the Authorization header.
Links: [https://github.com/sigp/lighthouse/issues/2512](https://github.com/sigp/lighthouse/issues/2512)
Reported: 2021-08-13
Fixed Date: 2021-08-18
Published: 2021-12-01
Bounty Hunter: Taurus
Bounty Points: Part of EF initiated Security Audit: https://arxiv.org/abs/2109.11685
Bounty Reward (Usd): 0
