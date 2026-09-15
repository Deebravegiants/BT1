# [M] MantisBT may disclose project names to unauthorized users 

## Summary
Severity: Medium
Advisory: GHSA-v642-mh27-8j6m
CVE: CVE-2023-44394
CWE: CWE-200, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-v642-mh27-8j6m
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.25.8

## Details
### Impact

Due to insufficient access-level checks on the Wiki redirection page, any user can reveal private Projects' names, by accessing wiki.php with sequentially incremented IDs.

### Patches
The vulnerability has been fixed in MantisBT version 2.25.8 (https://github.com/mantisbt/mantisbt/commit/65c44883f9d24f3ccef066fb523c93d8fdd7afc1).

### Workarounds
Disable wiki integration ( `$g_wiki_enable = OFF;`)

### References
- https://mantisbt.org/bugs/view.php?id=32981

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-v642-mh27-8j6m
- https://nvd.nist.gov/vuln/detail/CVE-2023-44394
- https://github.com/mantisbt/mantisbt/commit/65c44883f9d24f3ccef066fb523c93d8fdd7afc1
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=32981
