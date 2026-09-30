# [M] Eclipse Wakaama CoAP Block1 Handler Unbounded Memory Allocation DoS

## Summary
Severity: Medium
Advisory: CVE-2026-58465
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58465
Type: osv

## Details
Eclipse Wakaama before snapshot/2026-05-26 contains an unbounded memory allocation vulnerability in the CoAP Block1 handler within coap/block.c that allows unauthenticated remote attackers to exhaust server memory by sending a sequence of Block1 PUT requests with incrementing block numbers. Attackers can target the registration endpoint over UDP without authentication, causing the server to repeatedly reallocate a growing accumulation buffer by appending each block payload without enforcing any maximum total size limit, resulting in denial of service through memory exhaustion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58465.json
- https://github.com/eclipse-wakaama/wakaama/releases/tag/snapshots%2F2026-05-26
- https://nvd.nist.gov/vuln/detail/CVE-2026-58465
- https://www.vulncheck.com/advisories/eclipse-wakaama-coap-block1-handler-unbounded-memory-allocation-dos
- https://github.com/eclipse-wakaama/wakaama/pull/881
- https://github.com/eclipse-wakaama/wakaama/commit/a83f1ca28fa090fbc03c3669fef40daf4f89cd03
- https://github.com/eclipse-wakaama/wakaama
