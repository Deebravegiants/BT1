# [M] 389-ds-base: server crash while modifying `userpassword` using malformed input (incomplete fix for cve-2024-2199)

## Summary
Severity: Medium
Advisory: CVE-2024-8445
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-09-05
Source: https://osv.dev/vulnerability/CVE-2024-8445
Type: osv

## Details
The fix for CVE-2024-2199 in 389-ds-base was insufficient to cover all scenarios. In certain product versions, an authenticated user may cause a server crash while modifying `userPassword` using malformed input.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00015.html
- https://access.redhat.com/errata/RHSA-2024:7434
- https://access.redhat.com/security/cve/CVE-2024-8445
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8445.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8445
- https://bugzilla.redhat.com/show_bug.cgi?id=2310110
- https://github.com/389ds/389-ds-base
