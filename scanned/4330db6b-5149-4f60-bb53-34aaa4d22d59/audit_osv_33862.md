# [M] CVE-2025-51823

## Summary
Severity: Medium
Advisory: CVE-2025-51823
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-51823
Type: osv

## Details
libcsp 2.0 is vulnerable to Buffer Overflow in the csp_eth_init() function due to improper handling of the ifname parameter. The function uses strcpy to copy the interface name into a structure member (ctx->name) without validating the input length.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51823.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51823
- https://github.com/libcsp/libcsp/issues/850
- https://github.com/libcsp/libcsp/pull/852
