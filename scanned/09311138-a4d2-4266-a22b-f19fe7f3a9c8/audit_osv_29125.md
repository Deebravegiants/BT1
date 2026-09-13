# [C] Authenticated remote code execution in Thruk

## Summary
Severity: Critical
Advisory: CVE-2024-39915
Aliases: GHSA-r7gx-h738-4w6f
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/CVE-2024-39915
Type: osv

## Details
Thruk is a multibackend monitoring webinterface for Naemon, Nagios, Icinga and Shinken using the Livestatus API. This authenticated RCE in Thruk allows authorized users with network access to inject arbitrary commands via the URL parameter during PDF report generation. The Thruk web application does not properly process the url parameter when generating a PDF report. An authorized attacker with access to the reporting functionality could inject arbitrary commands that would be executed when the script /script/html2pdf.sh is called. The vulnerability can be exploited by an authorized user with network access. This issue has been addressed in version 3.16. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39915.json
- https://github.com/sni/Thruk/security/advisories/GHSA-r7gx-h738-4w6f
- https://nvd.nist.gov/vuln/detail/CVE-2024-39915
- https://github.com/sni/Thruk/commit/7e7eb251e76718a07639c4781f0d959d817f173b
