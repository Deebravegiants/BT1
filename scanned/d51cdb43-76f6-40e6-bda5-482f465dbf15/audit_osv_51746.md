# [M] CVE-2021-39360

## Summary
Severity: Medium
Advisory: CVE-2021-39360
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-22
Source: https://osv.dev/vulnerability/CVE-2021-39360
Type: osv

## Details
In GNOME libzapojit through 0.0.3, zpj-skydrive.c does not enable TLS certificate verification on the SoupSessionSync objects it creates, leaving users vulnerable to network MITM attacks. NOTE: this is similar to CVE-2016-20011.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IDXCHOCVP3VSAKDBQSLER2DQHFIOUHAT/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TNSIMQXP6VQWJXI7VW7ZCLCS4NWW465T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UG7TUICJM4QJHI4QJ2RHOSQE2QWD3KO3/
- https://blogs.gnome.org/mcatanzaro/2021/05/25/reminder-soupsessionsync-and-soupsessionasync-default-to-no-tls-certificate-verification/
- https://gitlab.gnome.org/GNOME/libzapojit/-/issues/4
