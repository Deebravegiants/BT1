# [M] Mingsoft MCMS vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-p46c-m4j7-mjvq
CVE: CVE-2022-4350
CWE: CWE-79
Ecosystem: Maven
Published: 2022-12-08
Source: https://github.com/advisories/GHSA-p46c-m4j7-mjvq
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0

## Details
A vulnerability, which was classified as problematic, was found in Mingsoft MCMS 5.2.8. Affected is an unknown function of the file search.do. The manipulation of the argument content_title leads to cross site scripting. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. The identifier of this vulnerability is VDB-215112.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4350
- https://gitee.com/mingSoft/MCMS/issues/I5MT8Y
- https://github.com/ming-soft/MCMS
- https://vuldb.com/?id.215112
