# [H] Local Privilege Escalation in Nimble Commander <= v1.6.0, Build 4087

## Summary
Severity: High
Advisory: CVE-2024-7062
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/CVE-2024-7062
Type: osv

## Details
Nimble Commander suffers from a privilege escalation vulnerability due to the server (info.filesmanager.Files.PrivilegedIOHelperV2) performing improper/insufficient validation of a client’s authorization before executing an operation. Consequently, it is possible to execute system-level commands as the root user, such as changing permissions and ownership, obtaining a handle (file descriptor) of an arbitrary file, and terminating processes, among other operations.

## References
- https://pentraze.com/vulnerability-reports/CVE-2024-7062/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7062.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7062
- https://github.com/mikekazakov/nimble-commander
