# [C] CVE-2024-41184

## Summary
Severity: Critical
Advisory: CVE-2024-41184
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-18
Source: https://osv.dev/vulnerability/CVE-2024-41184
Type: osv

## Details
In the vrrp_ipsets_handler handler (fglobal_parser.c) of keepalived through 2.3.1, an integer overflow can occur. NOTE: this CVE Record might not be worthwhile because an empty ipset name must be configured by the user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41184.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41184
- https://github.com/acassen/keepalived/issues/2447#issuecomment-2231329734
