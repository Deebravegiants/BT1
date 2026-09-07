# [M] Moodle IDOR when accessing list of badge recipients

## Summary
Severity: Medium
Advisory: GHSA-g8r3-2v89-j6r5
CVE: CVE-2024-48900
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-g8r3-2v89-j6r5
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=4.4.0 <4.4.4

## Details
A vulnerability was found in Moodle. Additional checks are required to ensure users with permission to view badge recipients can only access lists of those they are intended to have access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48900
- https://bugzilla.redhat.com/show_bug.cgi?id=2318818
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=462879
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-83178
