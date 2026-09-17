# [H] Knowage-Server vulnerable to account validation bypass

## Summary
Severity: High
Advisory: CVE-2023-35154
Aliases: GHSA-48hp-jvv8-cf62
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2023-06-23
Source: https://osv.dev/vulnerability/CVE-2023-35154
Type: osv

## Details
Knowage is an open source analytics and business intelligence suite. Starting in version 6.0.0 and prior to version 8.1.8, an attacker can register and activate their account without having to click on the link included in the email, allowing them access to the application as a normal user. This issue has been patched in version 8.1.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35154.json
- https://github.com/KnowageLabs/Knowage-Server/security/advisories/GHSA-48hp-jvv8-cf62
- https://nvd.nist.gov/vuln/detail/CVE-2023-35154
