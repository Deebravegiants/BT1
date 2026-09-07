# [M] Browsershot version 3.57.3 vulnerable to improper input validation

## Summary
Severity: Medium
Advisory: GHSA-6q49-35h6-rq2p
CVE: CVE-2022-43984
CWE: CWE-20, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-25
Source: https://github.com/advisories/GHSA-6q49-35h6-rq2p
Type: github-advisory

## Affected
- Packagist: `spatie/browsershot` — affected >=0 <3.57.4

## Details
Browsershot version 3.57.3 allows an external attacker to remotely obtain arbitrary local files. This is possible because the application does not validate that the JS content imported from an external source passed to the Browsershot::html method does not contain URLs that use the file:// protocol.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43984
- https://github.com/spatie/browsershot/commit/554c3e566fde8c47ad1ac9be47eaeb9a84c4dfe2
- https://github.com/spatie/browsershot/commit/92cf16fc098211731f80d21687abeafbe2c457ad
- https://fluidattacks.com/advisories/malone
- https://github.com/spatie/browsershot
