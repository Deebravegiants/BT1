# [M] OOBR in rpcap client in libpcap before 1.10.7

## Summary
Severity: Medium
Advisory: CVE-2026-18238
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-18238
Type: osv

## Details
The rpcap client code that processes a RPCAP_MSG_PACKET message received from the server incorrectly validates its headers.  A malicious server can send a crafted message and cause the client to treat up to 20 bytes of the client process memory beyond the end of the buffer as if it was a part of the captured packet.

## References
- https://github.com/the-tcpdump-group/libpcap/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18238.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18238
- https://github.com/the-tcpdump-group/libpcap/commit/b9590d482986d64673712460aae1d48d11fa0473
