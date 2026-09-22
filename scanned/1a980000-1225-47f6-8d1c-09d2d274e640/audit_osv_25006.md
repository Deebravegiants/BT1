# [H] CVE-2023-29458

## Summary
Severity: High
Advisory: CVE-2023-29458
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-13
Source: https://osv.dev/vulnerability/CVE-2023-29458
Type: osv

## Details
Duktape is an 3rd-party embeddable JavaScript engine, with a focus on portability and compact footprint. When adding too many values in valstack JavaScript will crash. This issue occurs due to bug in Duktape 2.6 which is an 3rd-party solution that we use.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00000.html
- https://support.zabbix.com/browse/ZBX-22989
