# [C] Salt vulnerable to directory traversal attack in file receiving method

## Summary
Severity: Critical
Advisory: GHSA-8pcp-r83j-fc92
CVE: CVE-2024-38824
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-8pcp-r83j-fc92
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3007.0rc1 <3007.4
- PyPI: `salt` — affected >=3006.0rc1 <3006.12

## Details
Directory traversal vulnerability in recv_file method allows arbitrary files to be written to the master cache directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-38824
- https://github.com/saltstack/salt/commit/c4ad23f0f3132d8d8a88f19fa537dc42cf21b215
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
