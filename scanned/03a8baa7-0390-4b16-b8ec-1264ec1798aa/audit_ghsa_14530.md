# [C] Remote code execution in Funadmin

## Summary
Severity: Critical
Advisory: GHSA-7g53-jj25-jhgr
CVE: CVE-2023-24776
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-06
Source: https://github.com/advisories/GHSA-7g53-jj25-jhgr
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
Funadmin v3.2.0 was discovered to contain a remote code execution (RCE) vulnerability via the component \controller\Addon.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24776
- https://github.com/funadmin/funadmin/issues/7
- https://github.com/funadmin/funadmin
