# [M] CVE-2021-39359

## Summary
Severity: Medium
Advisory: CVE-2021-39359
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-22
Source: https://osv.dev/vulnerability/CVE-2021-39359
Type: osv

## Details
In GNOME libgda through 6.0.0, gda-web-provider.c does not enable TLS certificate verification on the SoupSessionSync objects it creates, leaving users vulnerable to network MITM attacks. NOTE: this is similar to CVE-2016-20011.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRPPP47WRCAPAEJGRMEKYYJZBQCYXTLQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WLMVVIJNY5NMOT3FH36RFBWOTPVW7GME/
- https://blogs.gnome.org/mcatanzaro/2021/05/25/reminder-soupsessionsync-and-soupsessionasync-default-to-no-tls-certificate-verification/
- https://gitlab.gnome.org/GNOME/libgda/-/issues/249
- https://github.com/GNOME/libgda/commit/bd7b9568bcd9f6d3e6680bb04323a670c842a62d
