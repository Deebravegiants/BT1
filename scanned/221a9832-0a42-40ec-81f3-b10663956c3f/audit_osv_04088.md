# [M] Apache HTTP Server: HTTP/2 stream memory not reclaimed right away on RST

## Summary
Severity: Medium
Advisory: BIT-apache-2023-45802
Aliases: CVE-2023-45802
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apache-2023-45802
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.17 <2.4.58

## Details
When a HTTP/2 stream was reset (RST frame) by a client, there was a time window were the request's memory resources were not reclaimed immediately. Instead, de-allocation was deferred to connection close. A client could send new requests and resets, keeping the connection busy and open and causing the memory footprint to keep on growing. On connection close, all resources were reclaimed, but the process might run out of memory before that.

This was found by the reporter during testing of CVE-2023-44487 (HTTP/2 Rapid Reset Exploit) with their own test client. During "normal" HTTP/2 use, the probability to hit this bug is very low. The kept memory would not become noticeable before the connection closes or times out.

Users are recommended to upgrade to version 2.4.58, which fixes the issue.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2MBEPPC36UBVOZZNAXFHKLFGSLCMN5LI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BFQD3KUEMFBHPAPBGLWQC34L4OWL5HAZ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WE2I52RHNNU42PX6NZ2RBUHSFFJ2LVZX/
- https://security.netapp.com/advisory/ntap-20231027-0011/
- https://lists.debian.org/debian-lts-announce/2024/05/msg00013.html
- https://nvd.nist.gov/vuln/detail/CVE-2023-45802
