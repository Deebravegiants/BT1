# [H] PimpMyLog 1.7.14 Improper Access Control via Account Creation Endpoint

## Summary
Severity: High
Advisory: CVE-2023-53895
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2023-53895
Type: osv

## Details
PimpMyLog 1.7.14 contains an improper access control vulnerability that allows remote attackers to create admin accounts without authorization through the configuration endpoint. Attackers can exploit the unsanitized username field to inject malicious JavaScript, create a hidden backdoor account, and potentially access sensitive server-side log information and environmental variables.

## References
- https://www.pimpmylog.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53895.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53895
- https://www.vulncheck.com/advisories/pimpmylog-improper-access-control-via-account-creation-endpoint
- https://github.com/potsky/PimpMyLog
- https://www.exploit-db.com/exploits/51593
