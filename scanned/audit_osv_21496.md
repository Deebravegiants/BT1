# [H] CVE-2021-43518

## Summary
Severity: High
Advisory: CVE-2021-43518
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-43518
Type: osv

## Details
Teeworlds up to and including 0.7.5 is vulnerable to Buffer Overflow. A map parser does not validate m_Channels value coming from a map file, leading to a buffer overflow. A malicious server may offer a specially crafted map that will overwrite client's stack causing denial of service or code execution.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JIYZ7EVY6NZBM7FQF6GVUARYO6MKSEAT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OS2LI2RHQNUKUT3FKWYHRC27PLRWCHMZ/
- https://github.com/teeworlds/teeworlds/issues/2981
- https://mmmds.pl/fuzzing-map-parser-part-1-teeworlds/
