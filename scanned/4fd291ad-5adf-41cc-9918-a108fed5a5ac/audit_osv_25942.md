# [M] Glibc: potential use-after-free in gaih_inet()

## Summary
Severity: Medium
Advisory: CVE-2023-4813
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-12
Source: https://osv.dev/vulnerability/CVE-2023-4813
Type: osv

## Details
A flaw has been identified in glibc. In an uncommon situation, the gaih_inet function may use memory that has been freed, resulting in an application crash. This issue is only exploitable when the getaddrinfo function is called and the hosts database in /etc/nsswitch.conf is configured with SUCCESS=continue or SUCCESS=merge.

## References
- http://www.openwall.com/lists/oss-security/2023/10/03/8
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHBA-2024:2413
- https://access.redhat.com/errata/RHSA-2023:5453
- https://access.redhat.com/errata/RHSA-2023:5455
- https://access.redhat.com/errata/RHSA-2023:7409
- https://access.redhat.com/security/cve/CVE-2023-4813
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4813.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4813
- https://security.netapp.com/advisory/ntap-20231110-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2237798
