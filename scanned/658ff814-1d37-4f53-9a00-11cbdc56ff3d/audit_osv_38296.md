# [H] CVE-2026-37460

## Summary
Severity: High
Advisory: CVE-2026-37460
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-37460
Type: osv

## Details
Missing input validation in the rfapiRibBi2Ri() function (rfapi_rib.c) of FRRouting (FRR) stable/10.0 to stable/10.6 allows attackers to cause a Denial of Service (DoS) via supplying a crafted BGP UPDATE message.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37460.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-37460
- https://github.com/FRRouting/frr/commit/7676cad65114aa23adde58
- https://github.com/FRRouting/frr/pull/21098%2C
- https://github.com/FRRouting/frr
