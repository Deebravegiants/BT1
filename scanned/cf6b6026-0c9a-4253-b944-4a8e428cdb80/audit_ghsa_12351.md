# [M] tokio-boring vulnerable to resource exhaustion via memory leak

## Summary
Severity: Medium
Advisory: GHSA-pjrj-h4fg-6gm4
CVE: CVE-2023-6180
CWE: CWE-400, CWE-401, CWE-404
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-pjrj-h4fg-6gm4
Type: github-advisory

## Affected
- crates.io: `tokio-boring` — affected >=4.0.0 <4.1.0

## Details
### Impact
The tokio-boring library in version 4.0.0 is affected by a memory leak issue that can lead to excessive resource consumption and potential DoS by resource exhaustion. The `set_ex_data` function used by the library did not deallocate memory used by pre-existing data in memory each time after completing a TLS connection causing the program to consume more resources with each new connection.

### Patches
The issue is fixed in version 4.1.0 of tokio-boring.

### References
[CVE-2023-6180 at cve.org](https://www.cve.org/CVERecord?id=CVE-2023-6180)

## References
- https://github.com/cloudflare/boring/security/advisories/GHSA-pjrj-h4fg-6gm4
- https://nvd.nist.gov/vuln/detail/CVE-2023-6180
- https://github.com/cloudflare/boring/commit/a32783374f2682e6949fdb713910b1b9f103d3ed
- https://github.com/cloudflare/boring
