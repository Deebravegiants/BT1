# [H] Shim: rce in http boot support may lead to secure boot bypass

## Summary
Severity: High
Advisory: CVE-2023-40547
CVSS: 8.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2023-40547
Type: osv

## Details
A remote code execution vulnerability was found in Shim. The Shim boot support trusts attacker-controlled values when parsing an HTTP response. This flaw allows an attacker to craft a specific malicious HTTP request, leading to a completely controlled out-of-bounds write primitive and complete system compromise. This flaw is only exploitable during the early boot phase, an attacker needs to perform a Man-in-the-Middle or compromise the boot server to be able to exploit this vulnerability successfully.

## References
- http://www.openwall.com/lists/oss-security/2024/01/26/1
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/05/msg00009.html
- https://access.redhat.com/errata/RHSA-2024:1834
- https://access.redhat.com/errata/RHSA-2024:1835
- https://access.redhat.com/errata/RHSA-2024:1873
- https://access.redhat.com/errata/RHSA-2024:1876
- https://access.redhat.com/errata/RHSA-2024:1883
- https://access.redhat.com/errata/RHSA-2024:1902
- https://access.redhat.com/errata/RHSA-2024:1903
- https://access.redhat.com/errata/RHSA-2024:1959
- https://access.redhat.com/errata/RHSA-2024:2086
- https://access.redhat.com/security/cve/CVE-2023-40547
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40547.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40547
- https://bugzilla.redhat.com/show_bug.cgi?id=2234589
