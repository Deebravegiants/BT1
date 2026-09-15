# [H] chia-blockchain tokens can be inflated to an arbitrary extent

## Summary
Severity: High
Advisory: GHSA-pvjg-jwp3-mrj5
CVE: CVE-2022-36447
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-30
Source: https://github.com/advisories/GHSA-pvjg-jwp3-mrj5
Type: github-advisory

## Affected
- PyPI: `chia-blockchain` — affected >=0

## Details
An inflation issue was discovered in Chia Network CAT1 Standard 1.0.0. Previously minted tokens minted on the Chia blockchain using the CAT1 standard can be inflated to an arbitrary extent by any holder of any amount of the token. The total amount of the token can be increased as high as the malicious actor pleases. This is true for every CAT1 on the Chia blockchain regardless of issuance rules. This attack is auditable on chain, so maliciously altered coins can potentially be marked by off-chain observers as malicious.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-36447
- https://chia.net
- https://github.com/Chia-Network/chia-blockchain
- https://github.com/pypa/advisory-database/tree/main/vulns/chia-blockchain/PYSEC-2022-43072.yaml
- https://www.chia.net/2022/07/25/upgrading-the-cat-standard.en.html
