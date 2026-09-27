# [H] Aperture Finance incident: Aperture Finance (Aperture LM) was exploited for approximately $3.67 million across Ethereum, Base, Arbitrum, and BSC. The root ca

## Summary
Severity: High
Target: Aperture Finance
Loss: $ 3,670,000
Attack method: Smart Contract Vulnerability
Published: 2026-01-25
Source: https://x.com/ApertureFinance/status/2015938720453820752
Type: slowmist-incident

## Details
Aperture Finance (Aperture LM) was exploited for approximately $3.67 million across Ethereum, Base, Arbitrum, and BSC. The root cause was an arbitrary-call vulnerability in its closed-source V3/V4 contracts due to insufficient input validation on low-level calls. Attackers abused existing user token and Uniswap V3 LP NFT approvals to drain funds via transferFrom operations. The team paused affected features, urged users to revoke approvals, and published a security incident analysis.
