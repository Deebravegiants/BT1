# [H] CVE-2017-18190

## Summary
Severity: High
Advisory: CVE-2017-18190
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-02-16
Source: https://osv.dev/vulnerability/CVE-2017-18190
Type: osv

## Details
A localhost.localdomain whitelist entry in valid_host() in scheduler/client.c in CUPS before 2.2.2 allows remote attackers to execute arbitrary IPP commands by sending POST requests to the CUPS daemon in conjunction with DNS rebinding. The localhost.localdomain name is often resolved via a DNS server (neither the OS nor the web browser is responsible for ensuring that localhost.localdomain is 127.0.0.1).

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00023.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00003.html
- https://usn.ubuntu.com/3577-1/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1048
- https://github.com/apple/cups/commit/afa80cb2b457bf8d64f775bed307588610476c41
