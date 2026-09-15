# [M] CVE-2023-47325

## Summary
Severity: Medium
Advisory: CVE-2023-47325
Aliases: GHSA-42g3-3jwm-63rx
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-47325
Type: osv

## Details
Silverpeas Core 6.3.1 administrative "Bin" feature is affected by broken access control. A user with low privileges is able to navigate directly to the bin, revealing all deleted spaces. The user can then restore or permanently delete the spaces.

## References
- https://github.com/RhinoSecurityLabs/CVEs/tree/master/CVE-2023-47325
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47325.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47325
