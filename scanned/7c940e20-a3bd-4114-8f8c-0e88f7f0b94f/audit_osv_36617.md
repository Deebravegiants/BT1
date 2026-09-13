# [H] Open eClass Unauthenticated IDOR Allows Access to Arbitrary User Files

## Summary
Severity: High
Advisory: CVE-2026-24773
Aliases: GHSA-63pm-pff4-xc9c
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24773
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, an Insecure Direct Object Reference (IDOR) vulnerability allows unauthenticated remote attackers to access personal files of other users by directly requesting predictable user identifiers. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24773.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-63pm-pff4-xc9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-24773
