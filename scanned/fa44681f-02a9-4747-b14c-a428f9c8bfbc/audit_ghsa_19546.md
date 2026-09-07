# [M] OctoPrint Authenticated Reverse Proxy Page Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-qw93-h6pf-226x
CVE: CVE-2025-32788
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-04-22
Source: https://github.com/advisories/GHSA-qw93-h6pf-226x
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.11.0

## Details
### Impact

OctoPrint versions up until and including 1.10.3 contain a vulnerability that allows an attacker to bypass the login redirect and directly access the rendered HTML of certain frontend pages. 

The impact on data exposure is minimal because, typically, data is loaded via API requests that correctly enforce user authentication. In the current codebase, cases where data is directly embedded in the page content are rare. However, one notable exception is the authenticated variant of the reverse proxy test page, which displays the IP addresses of configured reverse proxies. 

The primary risk lies in potential future modifications to the codebase that might incorrectly rely on the vulnerable internal functions for authentication checks, leading to security vulnerabilities.

### Patches

The vulnerability has been patched in version 1.11.0.

### Details

An authentication bypass vulnerability exists in the following functions defined in [octoprint/server/util/init.py](https://github.com/OctoPrint/OctoPrint/blob/d79a0d20f3f1c7f2edb56dedda3b70267a937e65/src/octoprint/server/util/__init__.py):

- `require_login`
- `require_login_with`
- `require_fresh_login_with`

By adding the HTTP header `X-Preemptive-Recording: yes` to HTTP requests, these functions allow requests to proceed without redirecting to the login screen, effectively bypassing the login mechanism in the frontend. However, this only grants access to frontend page content, while authenticated API endpoints still enforce proper session validation.

### Credits

This vulnerability was discovered and responsibly disclosed to OctoPrint by Jacopo Tediosi

## References
- https://github.com/OctoPrint/OctoPrint/security/advisories/GHSA-qw93-h6pf-226x
- https://nvd.nist.gov/vuln/detail/CVE-2025-32788
- https://github.com/OctoPrint/OctoPrint/commit/41ff431014edfa18ca1a01897b10463934dc7fc2
- https://github.com/OctoPrint/OctoPrint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2025-56.yaml
