# [H] OS Command Injection in baserCMS

## Summary
Severity: High
Advisory: GHSA-g39q-f4rm-85x4
CVE: CVE-2021-20682
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-g39q-f4rm-85x4
Type: github-advisory

## Affected
- Packagist: `baserproject/basercms` — affected >=0 <4.4.5

## Details
baserCMS versions prior to 4.4.5 allows a remote attacker with an administrative privilege to execute arbitrary OS commands via upload of malicious plugins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20682
- https://basercms.net/security/JVN64869876
- https://jvn.jp/en/jp/JVN64869876/index.html
