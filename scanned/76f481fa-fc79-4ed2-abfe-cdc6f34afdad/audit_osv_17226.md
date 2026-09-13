# [M] CVE-2020-13882

## Summary
Severity: Medium
Advisory: CVE-2020-13882
CVSS: 4.2 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2020-13882
Type: osv

## Details
CISOfy Lynis before 3.0.0 has Incorrect Access Control because of a TOCTOU race condition. The routine to check the log and report file permissions was not working as intended and could be bypassed locally. Because of the race, an unprivileged attacker can set up a log and report file, and control that up to the point where the specific routine is doing its check. After that, the file can be removed, recreated, and used for additional attacks.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JDCHEKNR3HPJRNHE5PYKFH5GNBADTPA7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UBFHIX6RTHCK37FXMAAXP4KGAMLUFDUD/
- https://cisofy.com/security/cve/cve-2020-13882/
- https://cwe.mitre.org/data/definitions/367.html
