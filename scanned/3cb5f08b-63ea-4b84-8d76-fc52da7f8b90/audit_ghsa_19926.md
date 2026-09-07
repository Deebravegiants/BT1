# [C] nadesiko3 vulnerable to OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-7249-8x22-4rg4
CVE: CVE-2022-42496
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-05
Source: https://github.com/advisories/GHSA-7249-8x22-4rg4
Type: github-advisory

## Affected
- npm: `nadesiko3` — affected >=0 <3.3.75

## Details
OS command injection vulnerability in Nako3edit, editor component of nadesiko3 (PC Version) v3.3.74 and earlier allows a remote attacker to obtain appkey of the product and execute an arbitrary OS command on the product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42496
- https://github.com/kujirahand/nadesiko3/issues/1325
- https://github.com/kujirahand/nadesiko3/issues/1347
- https://github.com/kujirahand/nadesiko3
- https://github.com/kujirahand/nadesiko3/releases/tag/3.3.75
- https://jvn.jp/en/jp/JVN56968681/index.html
