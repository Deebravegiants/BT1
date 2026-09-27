# [M] CVE-2021-39365

## Summary
Severity: Medium
Advisory: CVE-2021-39365
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-22
Source: https://osv.dev/vulnerability/CVE-2021-39365
Type: osv

## Details
In GNOME grilo though 0.3.13, grl-net-wc.c does not enable TLS certificate verification on the SoupSessionAsync objects it creates, leaving users vulnerable to network MITM attacks. NOTE: this is similar to CVE-2016-20011.

## References
- https://blogs.gnome.org/mcatanzaro/2021/05/25/reminder-soupsessionsync-and-soupsessionasync-default-to-no-tls-certificate-verification/
- https://lists.debian.org/debian-lts-announce/2021/09/msg00010.html
- https://www.debian.org/security/2021/dsa-4964
- https://gitlab.gnome.org/GNOME/grilo/-/issues/146
