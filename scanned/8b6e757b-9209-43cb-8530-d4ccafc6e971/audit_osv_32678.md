# [M] rofl0r/proxychains-ng <= 4.17 Stack-based Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2025-34451
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-18
Source: https://osv.dev/vulnerability/CVE-2025-34451
Type: osv

## Details
rofl0r/proxychains-ng versions up to and including 4.17 and prior to commit cc005b7 contain a stack-based buffer overflow vulnerability in the function proxy_from_string() located in src/libproxychains.c. When parsing crafted proxy configuration entries containing overly long username or password fields, the application may write beyond the bounds of fixed-size stack buffers, leading to memory corruption or crashes. This vulnerability may allow denial of service and, under certain conditions, could be leveraged for further exploitation depending on the execution environment and applied mitigations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34451.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34451
- https://www.vulncheck.com/advisories/rofl0r-proxychains-ng-stack-based-buffer-overflow
- https://github.com/rofl0r/proxychains-ng/issues/606
- https://github.com/httpsgithu/proxychains-ng/commit/cc005b7
- https://github.com/rofl0r/proxychains-ng
- https://github.com/marlinkcyber/advisories/blob/main/advisories/MCSAID-2025-008-proxychains-ng-stack-buffer-overflow-proxy_from_string.md
