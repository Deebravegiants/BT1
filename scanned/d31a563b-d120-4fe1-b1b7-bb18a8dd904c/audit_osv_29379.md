# [M] Apache CloudStack: Unauthorised Network List Access

## Summary
Severity: Medium
Advisory: CVE-2024-42222
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-08-07
Source: https://osv.dev/vulnerability/CVE-2024-42222
Type: osv

## Details
In Apache CloudStack 4.19.1.0, a regression in the network listing API allows unauthorised list access of network details for domain admin and normal user accounts. This vulnerability compromises tenant isolation, potentially leading to unauthorised access to network details, configurations and data.

Affected users are advised to upgrade to version 4.19.1.1 to address this issue. Users on older versions of CloudStack considering to upgrade, can skip 4.19.1.0 and upgrade directly to 4.19.1.1.

## References
- http://www.openwall.com/lists/oss-security/2024/08/06/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42222.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42222
- https://www.shapeblue.com/shapeblue-security-advisory-apache-cloudstack-security-releases-4-18-2-3-and-4-19-1-1/
- https://github.com/apache/cloudstack/issues/9456
- https://cloudstack.apache.org/blog/security-release-advisory-4.19.1.1-4.18.2.3
- https://lists.apache.org/thread/lxqtfd6407prbw3801hb4fz3ot3t8wlj
