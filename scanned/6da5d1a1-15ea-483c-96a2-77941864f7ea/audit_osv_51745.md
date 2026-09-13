# [M] CVE-2021-39358

## Summary
Severity: Medium
Advisory: CVE-2021-39358
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-22
Source: https://osv.dev/vulnerability/CVE-2021-39358
Type: osv

## Details
In GNOME libgfbgraph through 0.2.4, gfbgraph-photo.c does not enable TLS certificate verification on the SoupSessionSync objects it creates, leaving users vulnerable to network MITM attacks. NOTE: this is similar to CVE-2016-20011.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WXXAF56BYLSES4UCLXKFCODZXTNAZ2G6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GRCVZUNPTNFQQQCEZVP7RYY6OKHPDBC5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UYI47UX6S5PAOWVWQ2KID64MCTXTH7SE/
- https://blogs.gnome.org/mcatanzaro/2021/05/25/reminder-soupsessionsync-and-soupsessionasync-default-to-no-tls-certificate-verification/
- https://gitlab.gnome.org/GNOME/libgfbgraph/-/issues/17
