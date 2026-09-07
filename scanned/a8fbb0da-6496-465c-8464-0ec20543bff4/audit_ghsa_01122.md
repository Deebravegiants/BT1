# [H] DLL Injection in kerberos

## Summary
Severity: High
Advisory: GHSA-m2mx-rfpw-jghv
CVE: CVE-2020-13110
CWE: CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-m2mx-rfpw-jghv
Type: github-advisory

## Affected
- npm: `kerberos` — affected >=0 <1.0.0

## Details
Version of `kerberos` prior to 1.0.0 are vulnerable to DLL Injection. The package loads DLLs without specifying a full path. This may allow attackers to create a file with the same name in a folder that precedes the intended file in the DLL path search. Doing so would allow attackers to execute arbitrary code in the machine.


## Recommendation

Upgrade to version 1.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13110
- https://github.com/mongodb-js/kerberos
- https://medium.com/@kiddo_Ha3ker/dll-injection-attack-in-kerberos-npm-package-cb4b32031cd
- https://www.linkedin.com/posts/op-innovate_dll-injection-attack-in-kerberos-npm-package-activity-6667043749547253760-kVlW
- https://www.npmjs.com/advisories/1514
- https://www.op-c.net/2020/05/15/dll-injection-attack-in-kerberos-npm-package
