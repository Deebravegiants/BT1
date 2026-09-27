# [M] CVE-2019-18849

## Summary
Severity: Medium
Advisory: CVE-2019-18849
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-11
Source: https://osv.dev/vulnerability/CVE-2019-18849
Type: osv

## Details
In tnef before 1.4.18, an attacker may be able to write to the victim's .ssh/authorized_keys file via an e-mail message with a crafted winmail.dat application/ms-tnef attachment, because of a heap-based buffer over-read involving strdup.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RMKFSHPMOZL7MDWU5RYOTIBTRWSZ4Z6X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W7CPKBW4QZ4VIY4UXIUVUSHRJ4R2FROE/
- https://lists.debian.org/debian-lts-announce/2019/11/msg00035.html
- https://lists.debian.org/debian-lts-announce/2021/08/msg00025.html
- https://usn.ubuntu.com/4524-1/
- https://github.com/verdammelt/tnef/compare/1.4.17...1.4.18
- https://github.com/verdammelt/tnef/pull/40
