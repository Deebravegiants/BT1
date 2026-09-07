# [M] MantisBT may expose private issues' summaries to unauthorized users

## Summary
Severity: Medium
Advisory: GHSA-hf4x-6h87-hm79
CVE: CVE-2023-22476
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-hf4x-6h87-hm79
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.25.6

## Details
### Impact
Due to insufficient access-level checks, any logged-in user allowed to perform Group Actions can get access to the _Summary_ field of private Issues (i.e. having Private view status, or belonging to a private Project) via a crafted `bug_arr[]` parameter in *bug_actiongroup_ext.php*.

### Patches
The vulnerability has been fixed in MantisBT version 2.25.6. 

### Workarounds
None

### Credits
Thanks to [d3vpoo1](https://github.com/jrckmcsb) for reporting the issue.

### References
- https://mantisbt.org/bugs/view.php?id=31086

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-hf4x-6h87-hm79
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=31086
