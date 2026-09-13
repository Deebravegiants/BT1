# [M] ELOG configuration file authorization bypass

## Summary
Severity: Medium
Advisory: CVE-2025-64348
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N/MPR:N/MSC:H/MSI:H/MSA:H)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/CVE-2025-64348
Type: osv

## Details
ELOG allows an authenticated user to modify or overwrite the configuration file, resulting in denial of service. If the execute facility is specifically enabled with the "-x" command line flag, attackers could execute OS commands on the host machine. By default, ELOG is not configured to allow shell commands or self-registration.

## References
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2025/va-25-304-01.json
- https://www.cve.org/CVERecord?id=CVE-2025-64348
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64348.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64348
- https://bitbucket.org/ritt/elog/commits/7092ff64f6eb9521f8cc8c52272a020bf3730946
- https://bitbucket.org/ritt/elog/commits/f81e5695c40997322fe2713bfdeba459d9de09dc
