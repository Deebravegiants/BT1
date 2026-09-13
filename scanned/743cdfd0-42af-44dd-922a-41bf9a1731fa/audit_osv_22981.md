# [C] Remote Code Execution in Optica

## Summary
Severity: Critical
Advisory: CVE-2022-41875
Aliases: GHSA-cf87-4h6x-phh6
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-11-23
Source: https://osv.dev/vulnerability/CVE-2022-41875
Type: osv

## Details
A remote code execution (RCE) vulnerability in Optica allows unauthenticated attackers to execute arbitrary code via specially crafted JSON payloads. Specially crafted JSON payloads may lead to RCE (remote code execution) on the attacked system running Optica. The vulnerability was patched in v. 0.10.2, where the call to the function `oj.load` was changed to `oj.safe_load`.

## References
- https://github.com/ohler55/oj/blob/develop/pages/Security.md
- https://www.rubydoc.info/gems/oj/3.0.2/Oj.safe_load
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41875.json
- https://github.com/airbnb/optica/security/advisories/GHSA-cf87-4h6x-phh6
- https://nvd.nist.gov/vuln/detail/CVE-2022-41875
