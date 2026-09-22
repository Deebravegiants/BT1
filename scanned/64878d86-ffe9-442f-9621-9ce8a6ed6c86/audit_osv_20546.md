# [H] CVE-2021-34825

## Summary
Severity: High
Advisory: CVE-2021-34825
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-06-17
Source: https://osv.dev/vulnerability/CVE-2021-34825
Type: osv

## Details
Quassel through 0.13.1, when --require-ssl is enabled, launches without SSL or TLS support if a usable X.509 certificate is not found on the local system.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7ZFWRN5P2WG23MWMVAEVV3YBHGFJHDSW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JOFTSGJUJHCA3KGQBO6OZXWU7JFKVHMJ/
- https://github.com/quassel/quassel/pull/581
