# [H] CircuitVerse potential RCE vulnerability via Oj.load

## Summary
Severity: High
Advisory: CVE-2022-36038
Aliases: GHSA-8c8q-4h7g-4rp3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-06
Source: https://osv.dev/vulnerability/CVE-2022-36038
Type: osv

## Details
CircuitVerse is an open-source platform which allows users to construct digital logic circuits online. A remote code execution (RCE) vulnerability in CircuitVerse allows authenticated attackers to execute arbitrary code via specially crafted JSON payloads. This issue may lead to Remote Code Execution (RCE). A patch is available in commit number 7b3023a99499a7675f10f2c1d9effdf10c35fb6e. There are currently no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36038.json
- https://github.com/CircuitVerse/CircuitVerse/security/advisories/GHSA-8c8q-4h7g-4rp3
- https://nvd.nist.gov/vuln/detail/CVE-2022-36038
- https://github.com/CircuitVerse/CircuitVerse/commit/7b3023a99499a7675f10f2c1d9effdf10c35fb6e
