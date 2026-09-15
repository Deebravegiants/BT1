# [H] Gitk allows arbitrary command execution

## Summary
Severity: High
Advisory: CVE-2025-27614
Aliases: GHSA-g4v5-fjv9-mhhc
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-27614
Type: osv

## Details
Gitk is a Tcl/Tk based Git history browser. Starting with 2.41.0, a Git repository can be crafted in such a way that with some social engineering a user who has cloned the repository can be tricked into running any script (e.g., Bourne shell, Perl, Python, ...) supplied by the attacker by invoking gitk filename, where filename has a particular structure. The script is run with the privileges of the user. This vulnerability is fixed in 2.43.7, 2.44.4, 2.45.4, 2.46.4, 2.47.3, 2.48.2, 2.49.1, and 2.50.

## References
- http://www.openwall.com/lists/oss-security/2025/07/08/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27614.json
- https://github.com/j6t/gitk/security/advisories/GHSA-g4v5-fjv9-mhhc
- https://nvd.nist.gov/vuln/detail/CVE-2025-27614
- https://github.com/j6t/gitk/commit/8e3070aa5e331be45d4d03e3be41f84494fce129
