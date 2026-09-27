# [M] Expat Denial of Service via storeAtts() Quadratic Complexity

## Summary
Severity: Medium
Advisory: CVE-2026-66046
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-66046
Type: osv

## Details
Expat through 2.8.3 contains a denial of service vulnerability caused by quadratic algorithmic complexity in the storeAtts() function in xmlparse.c, where processing N specified attributes with non-normalized values triggers an O(N^2) linear scan of elementType->defaultAtts to determine CDATA status. A remote unauthenticated attacker can supply a single well-formed XML document of a few megabytes to an application parsing untrusted XML to cause excessive CPU consumption, resulting in denial of service without requiring authentication, external entity resolution, or non-default parser options.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66046.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66046
- https://www.vulncheck.com/advisories/expat-denial-of-service-via-storeatts-quadratic-complexity
- https://github.com/libexpat/libexpat/pull/1321
- https://github.com/libexpat/libexpat
