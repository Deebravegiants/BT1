# [C] CVE-2023-38323

## Summary
Severity: Critical
Advisory: CVE-2023-38323
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-26
Source: https://osv.dev/vulnerability/CVE-2023-38323
Type: osv

## Details
An issue was discovered in OpenNDS before 10.1.3. It fails to sanitize the status path script entry in the configuration file, allowing attackers that have direct or indirect access to this file to execute arbitrary OS commands.

## References
- https://github.com/openNDS/openNDS/blob/master/ChangeLog
- https://github.com/openNDS/openNDS/releases/tag/v10.1.3
- https://openwrt.org/docs/guide-user/services/captive-portal/opennds
- https://www.forescout.com/resources/sierra21-vulnerabilities
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/38xxx/CVE-2023-38323.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-38323
