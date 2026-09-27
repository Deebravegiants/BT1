# [M] Improper Access Control Issues Lead to Sensitive Data Exposure in Mautic

## Summary
Severity: Medium
Advisory: CVE-2024-2731
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-2731
Type: osv

## Details
Users with low privileges (all permissions deselected in the administrator permissions settings) can view certain pages that expose sensitive information such as company names, users' names and surnames, stage names, and monitoring campaigns and their descriptions. In addition, unprivileged users can see and edit the descriptions of tags. At the time of publication of the CVE no patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2731.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2731
- https://github.com/mautic/mautic
- https://huntr.com/bounties/4d72d300-92d6-4e3c-93d8-52fe47396ae0
