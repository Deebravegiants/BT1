# [M] CVE-2021-3447

## Summary
Severity: Medium
Advisory: CVE-2021-3447
Aliases: PYSEC-2021-107
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-01
Source: https://osv.dev/vulnerability/CVE-2021-3447
Type: osv

## Details
A flaw was found in several ansible modules, where parameters containing credentials, such as secrets, were being logged in plain-text on managed nodes, as well as being made visible on the controller node when run in verbose mode. These parameters were not protected by the no_log feature. An attacker can take advantage of this information to steal those credentials, provided when they have access to the log files containing them. The highest threat from this vulnerability is to data confidentiality. This flaw affects Red Hat Ansible Automation Platform in versions before 1.2.2 and Ansible Tower in versions before 3.8.2.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2MS4VPUYVLGSAKOX26IT52BSMEZRZ3KS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JBZ75MAMVQVZROPYHMRDQKPPVASP63DG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RUTGO4RS4ZXZSPBU2CHVPT75IAFVTTL3/
- https://bugzilla.redhat.com/show_bug.cgi?id=1939349
