# [M] Moodle Authenticated LFI risk in some misconfigured shared hosting environments

## Summary
Severity: Medium
Advisory: GHSA-q3cm-ccrm-2mr6
CVE: CVE-2024-34004
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-31
Source: https://github.com/advisories/GHSA-q3cm-ccrm-2mr6
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.3.0 <4.3.4
- Packagist: `moodle/moodle` — affected >=4.2.0 <4.2.7
- Packagist: `moodle/moodle` — affected >=0 <4.1.10

## Details
In a shared hosting environment that has been misconfigured to allow access to other users' content, a Moodle user with both access to restore wiki modules and direct access to the web server outside of the Moodle webroot could execute a local file include.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34004
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=458393
