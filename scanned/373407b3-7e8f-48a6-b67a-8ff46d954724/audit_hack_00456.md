# [M] Renegade incident: Renegade’s legacy V1 deployment on Arbitrum was exploited. The attacker took advantage of an unprotected initializer in the Dark P

## Summary
Severity: Medium
Target: Renegade
Loss: $ 209,000
Attack method: Smart Contract Vulnerability
Published: 2026-05-10
Source: https://x.com/renegade_fi/status/2053531772634427599?s=46
Type: slowmist-incident

## Details
Renegade’s legacy V1 deployment on Arbitrum was exploited. The attacker took advantage of an unprotected initializer in the Dark Pool proxy contract (combined with a faulty migration from April 2025 that left the version counter out of sync), injected malicious logic, and used delegatecall to drain approximately $209,000 worth of 27 different ERC-20 tokens from the proxy contract’s storage. The exploiter, acting as a whitehat, negotiated on-chain with the team. Renegade offered a 90/10 split (return 90%, keep 10% as a whitehat bounty, no legal action). The whitehat returned ~$190,000 within 45 minutes. The team confirmed the issue was isolated to the V1 Arbitrum deployment (which has been paused), all other deployments are safe, and all affected users will be made whole.
