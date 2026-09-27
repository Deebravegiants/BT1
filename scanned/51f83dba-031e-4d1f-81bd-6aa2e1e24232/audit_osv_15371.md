# [C] CVE-2019-15699

## Summary
Severity: Critical
Advisory: CVE-2019-15699
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-09-24
Source: https://osv.dev/vulnerability/CVE-2019-15699
Type: osv

## Details
An issue was discovered in app-layer-ssl.c in Suricata 4.1.4. Upon receiving a corrupted SSLv3 (TLS 1.2) packet, the parser function TLSDecodeHSHelloExtensions tries to access a memory region that is not allocated, because the expected length of HSHelloExtensions does not match the real length of the HSHelloExtensions part of the packet.

## References
- https://lists.openinfosecfoundation.org/pipermail/oisf-announce/
- https://suricata-ids.org/2019/09/24/suricata-4-1-5-released/
