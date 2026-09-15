# [M] Stack Buffer Overflow in iowow

## Summary
Severity: Medium
Advisory: CVE-2022-23462
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-21
Source: https://osv.dev/vulnerability/CVE-2022-23462
Type: osv

## Details
IOWOW is a C utility library and persistent key/value storage engine. Versions 1.4.15 and prior contain a stack buffer overflow vulnerability that allows for Denial of Service (DOS) when it parses scientific notation numbers present in JSON. A patch for this issue is available at commit a79d31e4cff1d5a08f665574b29fd885897a28fd in the `master` branch of the repository. There are no workarounds other than applying the patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23462.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23462
- https://securitylab.github.com/advisories/GHSL-2022-066_iowow/
- https://github.com/Softmotions/iowow/commit/a79d31e4cff1d5a08f665574b29fd885897a28fd
