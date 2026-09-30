# [M] Iperf3: possible denial of service

## Summary
Severity: Medium
Advisory: CVE-2023-7250
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2023-7250
Type: osv

## Details
A flaw was found in iperf, a utility for testing network performance using TCP, UDP, and SCTP. A malicious or malfunctioning client can send less than the expected amount of data to the iperf server, which can cause the server to hang indefinitely waiting for the remainder or until the connection gets closed. This will prevent other connections to the server, leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00027.html
- https://access.redhat.com/errata/RHSA-2024:4241
- https://access.redhat.com/errata/RHSA-2024:9185
- https://access.redhat.com/security/cve/CVE-2023-7250
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7250.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7250
- https://bugzilla.redhat.com/show_bug.cgi?id=2244707
