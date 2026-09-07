# [M] one-api Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wvcx-j62q-45qw
CVE: CVE-2025-3801
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-19
Source: https://github.com/advisories/GHSA-wvcx-j62q-45qw
Type: github-advisory

## Affected
- Go: `github.com/songquanpeng/one-api` — affected >=0

## Details
A vulnerability was found in songquanpeng one-api up to 0.6.10. It has been classified as problematic. This affects an unknown part of the component System Setting Handler. The manipulation of the argument Homepage Content leads to cross site scripting. It is possible to initiate the attack remotely. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3801
- https://github.com/songquanpeng/one-api
- https://github.com/yaowenxiao721/Poc/blob/main/One-API/One-API-poc.md
- https://vuldb.com/?ctiid.305655
- https://vuldb.com/?id.305655
- https://vuldb.com/?submit.554702
