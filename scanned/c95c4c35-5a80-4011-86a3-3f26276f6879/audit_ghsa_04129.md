# [M] uap-core Regular Expression Denial of Service issue

## Summary
Severity: Medium
Advisory: GHSA-fx7m-j728-mjw3
CVE: CVE-2018-20164
CWE: CWE-185
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2019-03-06
Source: https://github.com/advisories/GHSA-fx7m-j728-mjw3
Type: github-advisory

## Affected
- npm: `uap-core` — affected >=0 <0.6.0

## Details
An issue was discovered in regex.yaml (aka regexes.yaml) in UA-Parser UAP-Core before 0.6.0. A Regular Expression Denial of Service (ReDoS) issue allows remote attackers to overload a server by setting the User-Agent header in an HTTP(S) request to a value containing a long digit string. (The UAP-Core project contains the vulnerability, propagating to all implementations.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20164
- https://github.com/ua-parser/uap-core/issues/332
- https://github.com/ua-parser/uap-core/commit/010ccdc7303546cd22b9da687c29f4a996990014
- https://github.com/ua-parser/uap-core/commit/156f7e12b215bddbaf3df4514c399d683e6cdadc
- https://github.com/ua-parser/uap-core
- https://www.x41-dsec.de/lab/advisories/x41-2018-009-uaparser
