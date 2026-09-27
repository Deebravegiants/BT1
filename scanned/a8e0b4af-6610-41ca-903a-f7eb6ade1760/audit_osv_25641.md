# [M] Authenticated XXE Injection Via The File Editor

## Summary
Severity: Medium
Advisory: CVE-2023-40612
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:U/C:L/I:H/A:L)
Published: 2023-08-23
Source: https://osv.dev/vulnerability/CVE-2023-40612
Type: osv

## Details
In OpenMNS Horizon 31.0.8 and versions earlier than 32.0.2, the file editor which is accessible to any user with ROLE_FILESYSTEM_EDITOR privileges is vulnerable to XXE injection attacks. The solution is to upgrade to Meridian 2023.1.5 or Horizon 32.0.2 or newer. Meridian and Horizon installation instructions state that they are intended for installation within an organization's private networks and should not be directly accessible from the Internet. OpenNMS thanks Erik Wynter for reporting this issue.

## References
- https://docs.opennms.com/meridian/2023/releasenotes/changelog.html#releasenotes-changelog-Meridian-2023.1.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40612.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40612
- https://github.com/OpenNMS/opennms/pull/6288
- https://github.com/OpenNMS/opennms
