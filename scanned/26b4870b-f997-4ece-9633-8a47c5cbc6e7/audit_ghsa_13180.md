# [C] Searchor CLI's Search vulnerable to Arbitrary Code using Eval

## Summary
Severity: Critical
Advisory: GHSA-66m2-493m-crh2
CVE: CVE-2023-43364
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-66m2-493m-crh2
Type: github-advisory

## Affected
- PyPI: `searchor` — affected >=0 <2.4.2

## Details
An issue in Arjun Sharda's Searchor before version v.2.4.2 allows an attacker to
 execute arbitrary code via a crafted script to the eval() function in Searchor's src/searchor/main.py file, affecting the search feature in Searchor's CLI (Command Line Interface).

### Impact
Versions equal to, or below 2.4.1 are affected.

### Patches
Versions above, or equal to 2.4.2 have patched the vulnerability.

### References
https://github.com/nikn0laty/Exploit-for-Searchor-2.4.0-Arbitrary-CMD-Injection
https://github.com/nexis-nexis/Searchor-2.4.0-POC-Exploit-
https://github.com/jonnyzar/POC-Searchor-2.4.2
https://github.com/ArjunSharda/Searchor/pull/130

## References
- https://github.com/ArjunSharda/Searchor/security/advisories/GHSA-66m2-493m-crh2
- https://nvd.nist.gov/vuln/detail/CVE-2023-43364
- https://github.com/ArjunSharda/Searchor/pull/130
- https://github.com/ArjunSharda/Searchor/commit/16016506f7bf92b0f21f51841d599126d6fcd15b
- https://github.com/ArjunSharda/Searchor
- https://github.com/advisories/GHSA-66m2-493m-crh2
- https://github.com/nexis-nexis/Searchor-2.4.0-POC-Exploit-
- https://github.com/nikn0laty/Exploit-for-Searchor-2.4.0-Arbitrary-CMD-Injection
- https://github.com/pypa/advisory-database/tree/main/vulns/searchor/PYSEC-2023-262.yaml
