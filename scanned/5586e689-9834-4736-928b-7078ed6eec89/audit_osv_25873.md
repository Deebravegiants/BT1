# [M] Shadow-utils: possible password leak during passwd(1) change

## Summary
Severity: Medium
Advisory: CVE-2023-4641
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-27
Source: https://osv.dev/vulnerability/CVE-2023-4641
Type: osv

## Details
A flaw was found in shadow-utils. When asking for a new password, shadow-utils asks the password twice. If the password fails on the second attempt, shadow-utils fails in cleaning the buffer used to store the first entry. This may allow an attacker with enough access to retrieve the password from the memory.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00026.html
- https://access.redhat.com/errata/RHSA-2023:6632
- https://access.redhat.com/errata/RHSA-2023:7112
- https://access.redhat.com/errata/RHSA-2024:0417
- https://access.redhat.com/errata/RHSA-2024:2577
- https://access.redhat.com/security/cve/CVE-2023-4641
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4641.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4641
- https://bugzilla.redhat.com/show_bug.cgi?id=2215945
- https://github.com/shadow-maint/shadow
