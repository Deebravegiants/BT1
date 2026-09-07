# [H] Regular Expression Denial of Service in Headers

## Summary
Severity: High
Advisory: GHSA-r6ch-mqf9-qc9w
CVE: CVE-2023-24807
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-r6ch-mqf9-qc9w
Type: github-advisory

## Affected
- npm: `undici` — affected >=0 <5.19.1

## Details
### Impact
The `Headers.set()` and `Headers.append()` methods are vulnerable to Regular Expression Denial of Service (ReDoS) attacks when untrusted values are passed into the functions. This is due to the inefficient regular expression used to normalize the values in the `headerValueNormalize()` utility function.

### Patches

This vulnerability was patched in v5.19.1.

### Workarounds
There is no workaround. Please update to an unaffected version.

### References

* https://hackerone.com/bugs?report_id=1784449

### Credits

Carter Snook reported this vulnerability.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-r6ch-mqf9-qc9w
- https://nvd.nist.gov/vuln/detail/CVE-2023-24807
- https://github.com/nodejs/undici/commit/f2324e549943f0b0937b09fb1c0c16cc7c93abdf
- https://github.com/nodejs/undici
- https://github.com/nodejs/undici/releases/tag/v5.19.1
- https://hackerone.com/bugs?report_id=1784449
