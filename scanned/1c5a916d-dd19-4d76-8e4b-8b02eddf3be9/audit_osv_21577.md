# [H] CVE-2021-44273

## Summary
Severity: High
Advisory: CVE-2021-44273
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-44273
Type: osv

## Details
e2guardian v5.4.x <= v5.4.3r is affected by missing SSL certificate validation in the SSL MITM engine. In standalone mode (i.e., acting as a proxy or a transparent proxy), with SSL MITM enabled, e2guardian, if built with OpenSSL v1.1.x, did not validate hostnames in certificates of the web servers that it connected to, and thus was itself vulnerable to MITM attacks.

## References
- https://lists.debian.org/debian-lts-announce/2023/09/msg00010.html
- http://www.openwall.com/lists/oss-security/2021/12/23/2
- https://github.com/e2guardian/e2guardian/commit/eae46a7e2a57103aadca903c4a24cca94dc502a2
- https://github.com/e2guardian/e2guardian/issues/707
