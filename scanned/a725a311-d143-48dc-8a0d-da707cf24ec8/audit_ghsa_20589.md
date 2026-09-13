# [C] Arbitrary code execution in H2 Console

## Summary
Severity: Critical
Advisory: GHSA-45hx-wfhj-473x
CVE: CVE-2022-23221
CWE: CWE-88
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-45hx-wfhj-473x
Type: github-advisory

## Affected
- Maven: `com.h2database:h2` — affected >=0 <2.1.210

## Details
H2 Console before 2.1.210 allows remote attackers to execute arbitrary code via a jdbc:h2:mem JDBC URL containing the IGNORE_UNKNOWN_SETTINGS=TRUE;FORBID_CREATION=FALSE;INIT=RUNSCRIPT substring, a different vulnerability than CVE-2021-42392.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23221
- https://github.com/h2database/h2database
- https://github.com/h2database/h2database/releases/tag/version-2.1.210
- https://github.com/h2database/h2database/security/advisories
- https://lists.debian.org/debian-lts-announce/2022/02/msg00017.html
- https://security.netapp.com/advisory/ntap-20230818-0011
- https://twitter.com/d0nkey_man/status/1483824727936450564
- https://www.debian.org/security/2022/dsa-5076
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://packetstormsecurity.com/files/165676/H2-Database-Console-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2022/Jan/39
