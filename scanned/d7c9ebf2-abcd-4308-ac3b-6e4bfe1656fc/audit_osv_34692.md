# [M] CVE-2025-63938

## Summary
Severity: Medium
Advisory: CVE-2025-63938
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-63938
Type: osv

## Details
Tinyproxy through 1.11.2 contains an integer overflow vulnerability in the strip_return_port() function within src/reqs.c.

## References
- https://github.com/rayinaw/my-hub/blob/main/CVE-2025-63938/DISCLOSURE.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63938.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63938
- https://github.com/tinyproxy/tinyproxy/issues/586
- https://github.com/tinyproxy/tinyproxy/commit/3c0fde94981b025271ffa1788ae425257841bf5a
