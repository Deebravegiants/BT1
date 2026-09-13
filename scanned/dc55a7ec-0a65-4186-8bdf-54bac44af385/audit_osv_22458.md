# [H] bt: host: Wrong key validation check

## Summary
Severity: High
Advisory: CVE-2022-2993
Aliases: GHSA-3286-jgjx-8cvr
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2022-12-09
Source: https://osv.dev/vulnerability/CVE-2022-2993
Type: osv

## Details
There is an error in the condition of the last if-statement in the function smp_check_keys. It was rejecting current keys if all requirements were unmet.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2993.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-3286-jgjx-8cvr
- https://nvd.nist.gov/vuln/detail/CVE-2022-2993
