# [M] Veracode Scan Jenkins Plugin vulnerable to information disclosure

## Summary
Severity: Medium
Advisory: GHSA-c4jr-vjm4-27hq
CVE: CVE-2023-25721
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-c4jr-vjm4-27hq
Type: github-advisory

## Affected
- Maven: `com.veracode.jenkins:veracode-scan` — affected >=0 <23.3.19.0

## Details
Veracode Scan Jenkins Plugin before 23.3.19.0 is vulnerable to information disclosure of proxy credentials in job logs under specific configurations.

Users are potentially affected if they:
- are using Veracode Scan Jenkins Plugin prior to 23.3.19.0
- AND have configured Veracode Scan to run on remote agent jobs
- AND have enabled the "Connect using proxy" option
- AND have configured the proxy settings with proxy credentials
- AND a Jenkins admin has enabled debug in global system settings.

By default, even in this configuration only the job owner or Jenkins admin can view the job log.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25721
- https://community.veracode.com/s/spotlight/frequently-asked-questions-for-cve-2023-25721-and-cve-2023-25722-MCFT34TH6OGRFR7F7JGDQQP4TNZE
- https://docs.veracode.com/updates/r/c_all_int#veracode-jenkins-plugin-233190
- https://github.com/jenkinsci/veracode-scan-plugin
- https://veracode.com
