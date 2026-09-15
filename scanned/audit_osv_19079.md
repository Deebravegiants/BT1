# [M] CVE-2020-7041

## Summary
Severity: Medium
Advisory: CVE-2020-7041
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-7041
Type: osv

## Details
An issue was discovered in openfortivpn 1.11.0 when used with OpenSSL 1.0.2 or later. tunnel.c mishandles certificate validation because an X509_check_host negative error code is interpreted as a successful return value.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CKNKSGBVYGRRVRLFEFBEKUEJYJR5LWOF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FF6HYIBREQGATRM5COF57MRQWKOKCWZ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SRVVNXCNTNMPCIAZIVR4FAGYCSU53FNA/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00011.html
- https://github.com/adrienverge/openfortivpn/issues/536
- https://github.com/adrienverge/openfortivpn/commit/60660e00b80bad0fadcf39aee86f6f8756c94f91
- https://github.com/adrienverge/openfortivpn/commit/cd9368c6a1b4ef91d77bb3fdbe2e5bc34aa6f4c4
