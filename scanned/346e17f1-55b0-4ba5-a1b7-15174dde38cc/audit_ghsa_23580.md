# [M] Moodle Ability to delete glossary entries that belong to another glossary

## Summary
Severity: Medium
Advisory: GHSA-2mg9-hv69-897x
CVE: CVE-2019-10187
CWE: CWE-284, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2mg9-hv69-897x
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.7 <3.7.1
- Packagist: `moodle/moodle` — affected >=3.6 <3.6.5
- Packagist: `moodle/moodle` — affected >=3.5 <3.5.7

## Details
A flaw was found in moodle before versions 3.7.1, 3.6.5, 3.5.7. Users with permission to delete entries from a glossary were able to delete entries from other glossaries they did not have direct access to.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10187
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10187
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=388568#p1566330
- http://www.securityfocus.com/bid/109174
