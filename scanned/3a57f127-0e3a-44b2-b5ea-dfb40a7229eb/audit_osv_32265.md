# [M] SSH SFTP packet size not verified properly in Erlang OTP

## Summary
Severity: Medium
Advisory: CVE-2025-26618
Aliases: GHSA-78cv-45vx-q6fr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-26618
Type: osv

## Details
Erlang is a programming language and runtime system for building massively scalable soft real-time systems with requirements on high availability. OTP is a set of Erlang libraries, which consists of the Erlang runtime system, a number of ready-to-use components mainly written in Erlang. Packet size is not verified properly for SFTP packets. As a result when multiple SSH packets (conforming to max SSH packet size) are received by ssh, they might be combined into an SFTP packet which will exceed the max allowed packet size and potentially cause large amount of memory to be allocated. Note that situation described above can only happen for successfully authenticated users after completing the SSH handshake. This issue has been patched in OTP versions 27.2.4, 26.2.5.9, and 25.3.2.18. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00028.html
- https://erlang.org/download/OTP-27.2.4.README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26618.json
- https://github.com/erlang/otp/security/advisories/GHSA-78cv-45vx-q6fr
- https://nvd.nist.gov/vuln/detail/CVE-2025-26618
- https://github.com/erlang/otp/commit/0ed2573cbd55c92e9125c9dc70fa1ca7fed82872
