# [H] CVE-2026-60007

## Summary
Severity: High
Advisory: CVE-2026-60007
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-60007
Type: osv

## Details
In Eclipse Milo versions 0.6.0 through 1.1.4, username-token processing returns distinguishable errors for invalid RSA PKCS#1 v1.5 padding and other authentication failures, allowing an on-path attacker who captures a victim's `Basic128Rsa15`-encrypted username token to use repeated unauthenticated `ActivateSession` requests as a padding oracle, recover the victim's password, and authenticate with the recovered credentials.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/183
- https://gitlab.eclipse.org/security/vulnerability-reports/-/work_items/598
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/60xxx/CVE-2026-60007.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-60007
- https://github.com/eclipse-milo/milo/commit/db59fae993a3a1bc66fffc8a2796d444b40285fb
