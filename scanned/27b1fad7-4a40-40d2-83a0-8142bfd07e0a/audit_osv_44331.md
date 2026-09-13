# [M] Stalled popup navigation could allow address bar origin spoofing in Firefox for iOS

## Summary
Severity: Medium
Advisory: CVE-2026-81267
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-81267
Type: osv

## Details
A malicious webpage could stall a popup's cross-origin navigation after commit, causing the address bar to display the destination origin while continuing to render attacker-controlled content. This vulnerability was fixed in Firefox for iOS 155.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81267.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81267
- https://www.mozilla.org/security/advisories/mfsa2026-81/
- https://bugzilla.mozilla.org/show_bug.cgi?id=2052758
