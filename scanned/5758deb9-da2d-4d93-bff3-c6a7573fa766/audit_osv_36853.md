# [M] Apache Ivy: PackagerResolver path traversal vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-26032
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-26032
Type: osv

## Details
The PackagerResolver of Apache Ivy is able to download online
artifacts and to (re)package them in a format defined by a
packager.xml file. This repackaging is done by an Ant script, which is
stored in a subdirectory of the configured "buildRoot" directory. This
subdirectory is calculated based on modules coordinates, like the
organisation, name or version.

If one of the coordinates contains "../" sequences - which are valid
characters for Ivy coordinates in general- it is possible to break out
of the configured "buildRoot" directory where other files can be
overwritten.

In order to exploit this vulnerability an attacker needs to have
access to a packager repository and add or modify the coordinates in
ivy.xml files to have such "../" sequences.

Users of Apache Ivy 2.0.0 to 2.5.3 (inclusive) should upgrade to Ivy 2.6.0.

## References
- http://www.openwall.com/lists/oss-security/2026/07/15/5
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26032.json
- https://lists.apache.org/thread/4d9dzrlnoplvywnyj9x6w84kxg7n3jyq
- https://nvd.nist.gov/vuln/detail/CVE-2026-26032
