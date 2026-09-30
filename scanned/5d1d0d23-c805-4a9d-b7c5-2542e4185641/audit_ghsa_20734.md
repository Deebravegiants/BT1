# [M] Regular expression denial of service in eth-account

## Summary
Severity: Medium
Advisory: GHSA-v65g-f3cj-fjp4
CVE: CVE-2022-1930
CWE: CWE-1333, CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-23
Source: https://github.com/advisories/GHSA-v65g-f3cj-fjp4
Type: github-advisory

## Affected
- PyPI: `eth-account` — affected >=0 <0.5.9

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the eth-account PyPI package, when an attacker is able to supply arbitrary input to the encode_structured_data method

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1930
- https://github.com/ethereum/eth-account/commit/70f89be700df0d5f08ef696252c88741f8414060
- https://github.com/ethereum/eth-account
- https://research.jfrog.com/vulnerabilities/eth-account-redos-xray-248681
