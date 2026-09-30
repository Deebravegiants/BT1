# [M] Network-AI before 5.13.4 Cryptographic Signature Verification Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-64623
Aliases: GHSA-3jf7-33vc-hgf4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64623
Type: osv

## Details
Network-AI before 5.13.4 contains an improper cryptographic signature verification vulnerability in APSAdapter where the default local verifier accepts any non-empty string as valid. Unauthenticated attackers can submit forged APS delegation payloads with arbitrary scopes to bypass signature verification and obtain signed permission-grant tokens for sensitive resources including SHELL_EXEC.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64623.json
- https://github.com/Jovancoding/Network-AI/security/advisories/GHSA-3jf7-33vc-hgf4
- https://nvd.nist.gov/vuln/detail/CVE-2026-64623
- https://www.vulncheck.com/advisories/network-ai-before-cryptographic-signature-verification-bypass
