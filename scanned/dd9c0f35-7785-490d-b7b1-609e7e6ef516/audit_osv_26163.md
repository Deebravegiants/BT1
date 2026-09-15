# [H] CVE-2023-52152

## Summary
Severity: High
Advisory: CVE-2023-52152
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-28
Source: https://osv.dev/vulnerability/CVE-2023-52152
Type: osv

## Details
mupnp/net/uri.c in mUPnP for C through 3.0.2 has an out-of-bounds read and application crash because it lacks a certain host length recalculation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52152.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52152
- https://github.com/cybergarage/mupnp/issues/21
