# [H] CVE-2022-44009

## Summary
Severity: High
Advisory: CVE-2022-44009
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/CVE-2022-44009
Type: osv

## Details
Improper access control in Key-Value RBAC in StackStorm version 3.7.0 didn't check the permissions in Jinja filters, allowing attackers to access K/V pairs of other users, potentially leading to the exposure of sensitive Information.

## References
- https://stackstorm.com/2022/12/v3-8-0-released/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44009.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44009
