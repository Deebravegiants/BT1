# [C] CVE-2020-7043

## Summary
Severity: Critical
Advisory: CVE-2020-7043
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-7043
Type: osv

## Details
An issue was discovered in openfortivpn 1.11.0 when used with OpenSSL before 1.0.2. tunnel.c mishandles certificate validation because hostname comparisons do not consider '\0' characters, as demonstrated by a good.example.com\x00evil.example.com attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CKNKSGBVYGRRVRLFEFBEKUEJYJR5LWOF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FF6HYIBREQGATRM5COF57MRQWKOKCWZ3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SRVVNXCNTNMPCIAZIVR4FAGYCSU53FNA/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00011.html
- https://github.com/adrienverge/openfortivpn/issues/536
- https://github.com/adrienverge/openfortivpn/commit/6328a070ddaab16faaf008cb9a8a62439c30f2a8
- https://github.com/adrienverge/openfortivpn/commit/cd9368c6a1b4ef91d77bb3fdbe2e5bc34aa6f4c4
