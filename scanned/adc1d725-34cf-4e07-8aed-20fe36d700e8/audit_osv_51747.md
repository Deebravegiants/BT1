# [M] CVE-2021-39361

## Summary
Severity: Medium
Advisory: CVE-2021-39361
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-22
Source: https://osv.dev/vulnerability/CVE-2021-39361
Type: osv

## Details
In GNOME evolution-rss through 0.3.96, network-soup.c does not enable TLS certificate verification on the SoupSessionSync objects it creates, leaving users vulnerable to network MITM attacks. NOTE: this is similar to CVE-2016-20011.

## References
- https://blogs.gnome.org/mcatanzaro/2021/05/25/reminder-soupsessionsync-and-soupsessionasync-default-to-no-tls-certificate-verification/
- https://gitlab.gnome.org/GNOME/evolution-rss/-/issues/11
