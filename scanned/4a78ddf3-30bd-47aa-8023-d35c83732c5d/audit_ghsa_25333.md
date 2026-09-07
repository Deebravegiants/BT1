# [C] LinOTP replay vulnerability with auto resynchronization enabled for TOTP token

## Summary
Severity: Critical
Advisory: GHSA-rqg8-xjp2-pg9w
CVE: CVE-2019-12887
CWE: CWE-294
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rqg8-xjp2-pg9w
Type: github-advisory

## Affected
- PyPI: `LinOTP` — affected >=0 <2.11.1

## Details
LinOTP is prone to a replay attack with activated automatic resynchronization. This vulnerability may allow an attacker to successfully log in with OTP values recorded at a previous point in time.

This attack is only possible if automatic resynchronization is enabled for the TOTP token type. The automatic resynchronization  is deactivated by default. All other tokens are unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12887
- https://github.com/LinOTP/LinOTP/commit/6d28d93af59d2ce0d844a6a3282148064efc6ad8
- https://github.com/LinOTP/LinOTP
- https://github.com/pypa/advisory-database/tree/main/vulns/linotp/PYSEC-2019-103.yaml
- https://linotp.org/linotp-hotfix-autoresync.html
- https://www.linotp.org/CVE-2019-12887.txt
