# [M] infinite loop in the PPP printer of tcpdump

## Summary
Severity: Medium
Advisory: CVE-2024-2397
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-12
Source: https://osv.dev/vulnerability/CVE-2024-2397
Type: osv

## Details
Due to a bug in packet data buffers management, the PPP printer in tcpdump can enter an infinite loop when reading a crafted DLT_PPP_SERIAL .pcap savefile.  This problem does not affect any tcpdump release, but it affected the git master branch from 2023-06-05 to 2024-03-21.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GEZRGR3QCW2ZNFIAWMZZOG4ZLFLFNG2M/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HUUI2MBVHFENXNBCHDQZP2RBBA2VD5HG/
- https://lists.freebsd.org/archives/freebsd-security/2024-September/000298.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2397.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2397
- https://github.com/the-tcpdump-group/tcpdump/commit/b9811ef5bb1b7d45a90e042f81f3aaf233c8bcb2
