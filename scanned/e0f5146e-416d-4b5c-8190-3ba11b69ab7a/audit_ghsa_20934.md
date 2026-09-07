# [M] Moodle Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fm6m-fg23-67jq
CVE: CVE-2021-36568
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-fm6m-fg23-67jq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0
- Packagist: `moodle/moodle` — affected >=3.10.0
- Packagist: `moodle/moodle` — affected >=3.11.0 <3.11.10

## Details
In certain Moodle products after creating a course, it is possible to add in a arbitrary "Topic" a resource, in this case a "Database" with the type "Text" where its values "Field name" and "Field description" are vulnerable to Cross Site Scripting Stored(XSS). This affects Moodle 3.11.x prior to 3.11.10, Moodle 3.10.4, and Moodle 3.9.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36568
- https://blog.hackingforce.com.br/en/cve-2021-36568
- https://bugzilla.redhat.com/show_bug.cgi?id=2126857
- https://github.com/moodle/moodle
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ERQ3NHVOK4ZXT4MS4LBQ2ZJHTON3LIMW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PRI4ETMQ4DJR3TZUOOGPBQ32RBD5LNGC
