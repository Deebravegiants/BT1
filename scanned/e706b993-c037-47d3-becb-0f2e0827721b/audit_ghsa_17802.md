# [C] Crayfish allows Remote Code Execution via Homarus Authorization header

## Summary
Severity: Critical
Advisory: GHSA-mm6v-68qp-f9fw
CVE: CVE-2025-25286
CWE: CWE-150, CWE-157
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-15
Source: https://github.com/advisories/GHSA-mm6v-68qp-f9fw
Type: github-advisory

## Affected
- Packagist: `islandora/crayfish` — affected >=0 <4.1.0

## Details
### Impact

Remote code execution may be possible in web-accessible installations of Homarus in certain configurations.

### Patches

The issue has been patched in `islandora/crayfish:4.1.0`

### Workarounds

The exploit requires making a request against the Homarus's `/convert` endpoint; therefore, the ability to exploit is much reduced if the microservice is not directly accessible from the Internet, so: Prevent general access from the Internet from hitting Homarus.

Configure auth in Crayfish to be more strongly required, such that requests with `Authorization` headers that do not validate are rejected before the problematic CLI interpolation occurs.

### References

- XBOW-024-071

## References
- https://github.com/Islandora/Crayfish/security/advisories/GHSA-mm6v-68qp-f9fw
- https://nvd.nist.gov/vuln/detail/CVE-2025-25286
- https://github.com/Islandora/Crayfish/commit/64cb4cec688928798cc40e6f0a0e863d7f69fd89
- https://github.com/Islandora/Crayfish
