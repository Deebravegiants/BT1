# [H] Apache Kylin vulnerable to Command injection by Useless configuration

## Summary
Severity: High
Advisory: GHSA-f5q9-j9r2-34gq
CVE: CVE-2022-43396
CWE: CWE-184, CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-f5q9-j9r2-34gq
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=2.0.0 <4.0.3

## Details
In the fix for CVE-2022-24697, a blacklist is used to filter user input commands. But there is a risk of being bypassed. The user can control the command by controlling the `kylin.engine.spark-cmd` parameter of `conf`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43396
- https://github.com/apache/kylin/pull/2011
- https://lists.apache.org/thread/ob2ks04zl5ms0r44cd74y1xdl1rzfd1r
