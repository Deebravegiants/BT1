# [H] setuptools vulnerable to Command Injection via package URL

## Summary
Severity: High
Advisory: GHSA-cx63-2mw6-8hw5
CVE: CVE-2024-6345
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-cx63-2mw6-8hw5
Type: github-advisory

## Affected
- PyPI: `setuptools` — affected >=0 <70.0.0

## Details
A vulnerability in the `package_index` module of pypa/setuptools versions up to 69.1.1 allows for remote code execution via its download functions. These functions, which are used to download packages from URLs provided by users or retrieved from package index servers, are susceptible to code injection. If these functions are exposed to user-controlled inputs, such as package URLs, they can execute arbitrary commands on the system. The issue is fixed in version 70.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6345
- https://github.com/pypa/setuptools/pull/4332
- https://github.com/pypa/setuptools/commit/88807c7062788254f654ea8c03427adc859321f0
- https://github.com/pypa/setuptools
- https://huntr.com/bounties/d6362117-ad57-4e83-951f-b8141c6e7ca5
- https://lists.debian.org/debian-lts-announce/2024/09/msg00018.html
