# [H] CVE-2020-7237

## Summary
Severity: High
Advisory: CVE-2020-7237
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-20
Source: https://osv.dev/vulnerability/CVE-2020-7237
Type: osv

## Details
Cacti 1.2.8 allows Remote Code Execution (by privileged users) via shell metacharacters in the Performance Boost Debug Log field of poller_automation.php. OS commands are executed when a new poller cycle begins. The attacker must be authenticated, and must have access to modify the Performance Settings of the product.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00048.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SUSOTOIEJKD2IWJHN7TY56TDZJQZJUVJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XLZAMGTW2OSIBLYLXWHQBGWP7M4DTRS7/
- https://ctrsec.io/index.php/2020/01/25/cve-2020-7237-remote-code-execution-in-cacti-rrdtool/
- https://security.gentoo.org/glsa/202003-40
- https://github.com/Cacti/cacti/issues/3201
