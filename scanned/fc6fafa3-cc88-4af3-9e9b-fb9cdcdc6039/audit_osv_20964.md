# [H] CVE-2021-39181

## Summary
Severity: High
Advisory: CVE-2021-39181
Aliases: GHSA-596v-3gwh-2m9w
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-01
Source: https://osv.dev/vulnerability/CVE-2021-39181
Type: osv

## Details
OpenOlat is a web-based learning management system (LMS). Prior to version 15.3.18, 15.5.3, and 16.0.0, using a prepared import XML file (e.g. a course) any class on the Java classpath can be instantiated, including spring AOP bean factories. This can be used to execute code arbitrary code by the attacker. The attack requires an OpenOlat user account with the authoring role. It can not be exploited by unregistered users. The problem is fixed in versions 15.3.18, 15.5.3, and 16.0.0. There are no known workarounds aside from upgrading.

## References
- https://github.com/OpenOLAT/OpenOLAT/security/advisories/GHSA-596v-3gwh-2m9w
- https://jira.openolat.org/browse/OO-5548
- https://github.com/OpenOLAT/OpenOLAT/commit/3f219ac457afde82e3be57bc614352ab92c05684
