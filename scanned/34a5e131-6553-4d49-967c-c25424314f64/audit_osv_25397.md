# [H] CVE-2023-35846

## Summary
Severity: High
Advisory: CVE-2023-35846
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-19
Source: https://osv.dev/vulnerability/CVE-2023-35846
Type: osv

## Details
VirtualSquare picoTCP (aka PicoTCP-NG) through 2.1 does not check the transport layer length in a frame before performing port filtering.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/35xxx/CVE-2023-35846.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-35846
- https://github.com/virtualsquare/picotcp/commit/d561990a358899178115e156871cc054a1c55ffe
