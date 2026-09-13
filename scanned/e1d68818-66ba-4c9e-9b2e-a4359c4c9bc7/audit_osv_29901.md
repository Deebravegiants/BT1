# [H] tranport: TLS host name wildcard matching too lax

## Summary
Severity: High
Advisory: CVE-2024-47619
Aliases: GHSA-xr54-gx74-fghg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-05-07
Source: https://osv.dev/vulnerability/CVE-2024-47619
Type: osv

## Details
syslog-ng is an enhanced log daemo. Prior to version 4.8.2, `tls_wildcard_match()` matches on certificates such as `foo.*.bar` although that is not allowed. It is also possible to pass partial wildcards such as `foo.a*c.bar` which glib matches but should be avoided / invalidated. This issue could have an impact on TLS connections, such as in man-in-the-middle situations. Version 4.8.2 contains a fix for the issue.

## References
- https://github.com/syslog-ng/syslog-ng/blob/b0ccc8952d333fbc2d97e51fddc0b569a15e7a7d/lib/transport/tls-verifier.c#L78-L110
- https://github.com/syslog-ng/syslog-ng/releases/tag/syslog-ng-4.8.2
- https://lists.debian.org/debian-lts-announce/2025/05/msg00034.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47619.json
- https://github.com/syslog-ng/syslog-ng/security/advisories/GHSA-xr54-gx74-fghg
- https://nvd.nist.gov/vuln/detail/CVE-2024-47619
- https://github.com/syslog-ng/syslog-ng/commit/dadfdbecde5bfe710b0a6ee5699f96926b3f9006
