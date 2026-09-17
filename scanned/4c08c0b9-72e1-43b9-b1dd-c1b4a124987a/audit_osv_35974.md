# [M] rpcapd memory leak in libpcap before 1.10.7

## Summary
Severity: Medium
Advisory: CVE-2026-18313
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-18313
Type: osv

## Details
rpcapd can allocate up to 65536 bytes per each RPCAP_MSG_UPDATEFILTER_REQ or RPCAP_MSG_STARTCAP_REQ message received from the client, but it never frees the memory, so it leaks memory even under normal use.  A malicious client can cause the server to leak memory substantially faster.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18313.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18313
- https://github.com/the-tcpdump-group/libpcap/commit/f9775af1a0ec76db60c7213241e6b48f1be10ac7
