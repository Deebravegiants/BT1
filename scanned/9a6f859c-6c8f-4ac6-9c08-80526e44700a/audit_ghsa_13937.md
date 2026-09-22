# [H] Denial of service due to unlimited number of parts

## Summary
Severity: High
Advisory: GHSA-hpp2-2cr5-pf6g
CVE: CVE-2023-25576
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-14
Source: https://github.com/advisories/GHSA-hpp2-2cr5-pf6g
Type: github-advisory

## Affected
- npm: `@fastify/multipart` — affected >=0 <6.0.1
- npm: `@fastify/multipart` — affected >=7.0.0 <7.4.1

## Details
### Impact

* The multipart body parser accepts an unlimited number of file parts.
* The multipart body parser accepts an unlimited number of field parts.
* The multipart body parser accepts an unlimited number of empty parts as field
parts.


### Patches

This is fixed in v7.4.1 (for Fastify v4.x) and v6.0.1 (for Fastify v3.x).

### Workarounds

There are no known workaround.  

### References

Reported at https://hackerone.com/reports/1816195.

## References
- https://github.com/fastify/fastify-multipart/security/advisories/GHSA-hpp2-2cr5-pf6g
- https://nvd.nist.gov/vuln/detail/CVE-2023-25576
- https://github.com/fastify/fastify-multipart/commit/85be81bedf5b29cfd9fe3efc30fb5a17173c1297
- https://hackerone.com/reports/1816195
- https://github.com/fastify/fastify-multipart
- https://github.com/fastify/fastify-multipart/releases/tag/v6.0.1
- https://github.com/fastify/fastify-multipart/releases/tag/v7.4.1
