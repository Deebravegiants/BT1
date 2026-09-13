# [M] Improper header validation in httpsoft/http-message

## Summary
Severity: Medium
Advisory: GHSA-9jxr-mwpp-w643
CWE: CWE-436
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-9jxr-mwpp-w643
Type: github-advisory

## Affected
- Packagist: `httpsoft/http-message` — affected >=0 <1.0.12

## Details
### Impact

Improper header parsing. An attacker could sneak in a newline (`\n`) into both the header names and values. While the specification states that `\r\n\r\n` is used to terminate the header list, many servers in the wild will also accept `\n\n`.

### Patches

The issue is patched in 1.0.12.

### Workarounds

There are no known workarounds.

### References

* https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4

## References
- https://github.com/guzzle/psr7/security/advisories/GHSA-wxmh-65f7-jcvw
- https://github.com/httpsoft/http-message/security/advisories/GHSA-9jxr-mwpp-w643
- https://nvd.nist.gov/vuln/detail/CVE-2023-29197
- https://github.com/httpsoft/http-message
