# [M] Open eClass's Active Sessions Not Invalidated After Password Change Allow Persistent Account Access

## Summary
Severity: Medium
Advisory: CVE-2026-24667
Aliases: GHSA-5h73-53mh-m224
CVSS: 5.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-24667
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, failure to invalidate active user sessions after a password change allows existing session tokens to remain valid, potentially enabling unauthorized continued access to user accounts. This issue has been patched in version 4.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24667.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-5h73-53mh-m224
- https://nvd.nist.gov/vuln/detail/CVE-2026-24667
