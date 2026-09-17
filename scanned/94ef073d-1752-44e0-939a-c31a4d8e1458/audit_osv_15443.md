# [C] CVE-2019-16239

## Summary
Severity: Critical
Advisory: CVE-2019-16239
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-17
Source: https://osv.dev/vulnerability/CVE-2019-16239
Type: osv

## Details
process_http_response in OpenConnect before 8.05 has a Buffer Overflow when a malicious server uses HTTP chunked encoding with crafted chunk sizes.

## References
- http://lists.infradead.org/pipermail/openconnect-devel/2019-September/005412.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FX56KYWC7X4ETV4P6HGJC7GZUEBITBBS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HDMZGNBLZZKAGBI2PNXYWWKLD2LXKFH6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WI7ZENFAWCHF2RU4NHPL2CU4WGZ4BNDJ/
- https://t2.fi/schedule/2019/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00061.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00003.html
- https://seclists.org/bugtraq/2020/Jan/31
- https://usn.ubuntu.com/4565-1/
- https://www.debian.org/security/2020/dsa-4607
