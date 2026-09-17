# [M] Requests vulnerable to .netrc credentials leak via malicious URLs

## Summary
Severity: Medium
Advisory: GHSA-9hjg-9r4m-mvj7
CVE: CVE-2024-47081
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-9hjg-9r4m-mvj7
Type: github-advisory

## Affected
- PyPI: `requests` — affected >=0 <2.32.4

## Details
### Impact

Due to a URL parsing issue, Requests releases prior to 2.32.4 may leak .netrc credentials to third parties for specific maliciously-crafted URLs.

### Workarounds
For older versions of Requests, use of the .netrc file can be disabled with `trust_env=False` on your Requests Session ([docs](https://requests.readthedocs.io/en/latest/api/#requests.Session.trust_env)).

### References
https://github.com/psf/requests/pull/6965
https://seclists.org/fulldisclosure/2025/Jun/2

## References
- https://github.com/psf/requests/security/advisories/GHSA-9hjg-9r4m-mvj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-47081
- https://github.com/psf/requests/pull/6965
- https://github.com/psf/requests/commit/96ba401c1296ab1dda74a2365ef36d88f7d144ef
- https://github.com/psf/requests
- https://requests.readthedocs.io/en/latest/api/#requests.Session.trust_env
- https://seclists.org/fulldisclosure/2025/Jun/2
- http://seclists.org/fulldisclosure/2025/Jun/2
- http://www.openwall.com/lists/oss-security/2025/06/03/11
- http://www.openwall.com/lists/oss-security/2025/06/03/9
- http://www.openwall.com/lists/oss-security/2025/06/04/1
- http://www.openwall.com/lists/oss-security/2025/06/04/6
