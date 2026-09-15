# [M] 389-ds-base: malformed userpassword may cause crash at do_modify in slapd/modify.c

## Summary
Severity: Medium
Advisory: CVE-2024-2199
CVSS: 5.7 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-2199
Type: osv

## Details
A denial of service vulnerability was found in 389-ds-base ldap server. This issue may allow an authenticated user to cause a server crash while modifying `userPassword` using malformed input.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00015.html
- https://www.port389.org/docs/389ds/releases/release-3-1-1.html
- https://access.redhat.com/errata/RHSA-2024:3591
- https://access.redhat.com/errata/RHSA-2024:3837
- https://access.redhat.com/errata/RHSA-2024:4092
- https://access.redhat.com/errata/RHSA-2024:4209
- https://access.redhat.com/errata/RHSA-2024:4210
- https://access.redhat.com/errata/RHSA-2024:4235
- https://access.redhat.com/errata/RHSA-2024:4633
- https://access.redhat.com/errata/RHSA-2024:5690
- https://access.redhat.com/errata/RHSA-2025:1632
- https://access.redhat.com/security/cve/CVE-2024-2199
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2199.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2199
- https://bugzilla.redhat.com/show_bug.cgi?id=2267976
- https://github.com/389ds/389-ds-base
