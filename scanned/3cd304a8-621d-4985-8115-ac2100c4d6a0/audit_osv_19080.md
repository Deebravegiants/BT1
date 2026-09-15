# [M] CVE-2020-7042

## Summary
Severity: Medium
Advisory: CVE-2020-7042
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-7042
Type: osv

## Details
An issue was discovered in openfortivpn 1.11.0 when used with OpenSSL 1.0.2 or later. tunnel.c mishandles certificate validation because the hostname check operates on uninitialized memory. The outcome is that a valid certificate is never accepted (only a malformed certificate may be accepted).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CKNKSGBVYGRRVRLFEFBEKUEJYJR5LWOF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FF6HYIBREQGATRM5COF57MRQWKOKCWZ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SRVVNXCNTNMPCIAZIVR4FAGYCSU53FNA/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00011.html
- https://github.com/adrienverge/openfortivpn/issues/536
- https://github.com/adrienverge/openfortivpn/commit/9eee997d599a89492281fc7ffdd79d88cd61afc3
- https://github.com/adrienverge/openfortivpn/commit/cd9368c6a1b4ef91d77bb3fdbe2e5bc34aa6f4c4
