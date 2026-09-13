# [M] CVE-2023-49345

## Summary
Severity: Medium
Advisory: CVE-2023-49345
Aliases: GHSA-rvhc-rch9-j943
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-49345
Type: osv

## Details
Temporary data passed between application components by Budgie Extras Takeabreak applet could potentially be viewed or manipulated. The data is stored in a location that is accessible to any user who has local access to the system. Attackers may pre-create and control this file to present false information to users or deny access to the application and panel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49345.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49345
- https://ubuntu.com/security/notices/USN-6556-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-49345
- https://github.com/UbuntuBudgie/budgie-extras/security/advisories/GHSA-rvhc-rch9-j943
