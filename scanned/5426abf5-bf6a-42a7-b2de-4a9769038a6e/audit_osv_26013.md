# [M] CVE-2023-49346

## Summary
Severity: Medium
Advisory: CVE-2023-49346
Aliases: GHSA-rffw-gg7p-5688
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-12-14
Source: https://osv.dev/vulnerability/CVE-2023-49346
Type: osv

## Details
Temporary data passed between application components by Budgie Extras WeatherShow applet could potentially be viewed or manipulated. The data is stored in a location that is accessible to any user who has local access to the system. Attackers may pre-create and control this file to present false information to users or deny access to the application and panel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49346.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49346
- https://ubuntu.com/security/notices/USN-6556-1
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2023-49346
- https://github.com/UbuntuBudgie/budgie-extras/security/advisories/GHSA-rffw-gg7p-5688
