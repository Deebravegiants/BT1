# [M] DayByDay CRM - Application-Wide Client-Side Template Injection (CSTI)

## Summary
Severity: Medium
Advisory: CVE-2022-22112
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2022-22112
Type: osv

## Details
In DayByDay CRM, versions 1.1 through 2.2.1 (latest) suffer from an application-wide Client-Side Template Injection (CSTI). A low privileged attacker can input template injection payloads in the application at various locations to execute JavaScript on the client browser.

## References
- https://github.com/Bottelet/DaybydayCRM/blob/2.2.1/resources/views/partials/clientheader.blade.php#L17
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2022-22112
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/22xxx/CVE-2022-22112.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-22112
