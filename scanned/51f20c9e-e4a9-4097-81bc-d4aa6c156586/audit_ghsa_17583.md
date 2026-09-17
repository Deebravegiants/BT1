# [M] Salt allows arbitrary directory creation or file deletion

## Summary
Severity: Medium
Advisory: GHSA-xh32-3m67-qjgf
CVE: CVE-2025-22240
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-13
Source: https://github.com/advisories/GHSA-xh32-3m67-qjgf
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=3007.0rc1 <3007.4
- PyPI: `salt` — affected >=3006.0rc1 <3006.12

## Details
Arbitrary directory creation or file deletion. In the find_file method of the GitFS class, a path is created using os.path.join using unvalidated input from the “tgt_env” variable. This can be exploited by an attacker to delete any file on the Master's process has permissions to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22240
- https://github.com/saltstack/salt/commit/f7c28ffbf18dbf693a15b1ba9493918de3e88cf3
- https://docs.saltproject.io/en/3006/topics/releases/3006.12.html
- https://docs.saltproject.io/en/3007/topics/releases/3007.4.html
- https://github.com/saltstack/salt
