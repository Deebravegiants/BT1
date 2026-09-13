# [H] CVE-2024-31031

## Summary
Severity: High
Advisory: CVE-2024-31031
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-31031
Type: osv

## Details
An issue in `coap_pdu.c` in libcoap 4.3.4 allows attackers to cause undefined behavior via a sequence of messages leading to unsigned integer overflow.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LPENEJBV3KSASIYKNZAKXDAH7Q66KPYG/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TUL7QDYFGEIJVO2ZSG4O5HEAWR6PFC52/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/31xxx/CVE-2024-31031.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LPENEJBV3KSASIYKNZAKXDAH7Q66KPYG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TUL7QDYFGEIJVO2ZSG4O5HEAWR6PFC52/
- https://nvd.nist.gov/vuln/detail/CVE-2024-31031
- https://github.com/obgm/libcoap/issues/1351
