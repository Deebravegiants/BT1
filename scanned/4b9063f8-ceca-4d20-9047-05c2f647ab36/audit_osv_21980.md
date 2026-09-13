# [M] sensitive data exposure in cloud-init logs

## Summary
Severity: Medium
Advisory: CVE-2022-2084
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2022-2084
Type: osv

## Details
Sensitive data could be exposed in world readable logs of cloud-init before version 22.3 when schema failures are reported. This leak could include hashed passwords.

## References
- https://github.com/canonical/cloud-init/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2084.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2084
- https://ubuntu.com/security/notices/USN-5496-1
- https://github.com/canonical/cloud-init/commit/4d467b14363d800b2185b89790d57871f11ea88c
- https://github.com/canonical/cloud-init/releases
