# [H] CVE-2023-23554

## Summary
Severity: High
Advisory: CVE-2023-23554
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-07
Source: https://osv.dev/vulnerability/CVE-2023-23554
Type: osv

## Details
Uncontrolled search path element vulnerability exists in pg_ivm versions prior to 1.5.1. When refreshing an IMMV, pg_ivm executes functions without specifying schema names. Under certain conditions, pg_ivm may be tricked to execute unexpected functions from other schemas with the IMMV owner's privilege. If this vulnerability is exploited, an unexpected function provided by an attacker may be executed with the privilege of the materialized view owner.

## References
- https://github.com/sraoss/pg_ivm/releases/tag/v1.5.1
- https://jvn.jp/en/jp/JVN19872280/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23554.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-23554
- https://github.com/sraoss/pg_ivm
