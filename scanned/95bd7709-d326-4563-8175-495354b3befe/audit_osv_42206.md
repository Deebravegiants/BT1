# [M] infinte loop in libpcap before 1.10.7

## Summary
Severity: Medium
Advisory: CVE-2026-6554
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-6554
Type: osv

## Details
libpcap BPF interpreter treats the offset in the 'ja L' BPF instruction as a signed integer to implement looping via backward jumps, but it does not limit the number of loop iterations.  In particular uncommon use cases a crafted filter program can cause the interpreter to loop infinitely.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6554.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6554
- https://github.com/the-tcpdump-group/libpcap/commit/ff3c83475ac303c6b681c52ad0b6e14795a8e0ce
