# [C] CVE-2018-6758

## Summary
Severity: Critical
Advisory: CVE-2018-6758
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-06
Source: https://osv.dev/vulnerability/CVE-2018-6758
Type: osv

## Details
The uwsgi_expand_path function in core/utils.c in Unbit uWSGI through 2.0.15 has a stack-based buffer overflow via a large directory length.

## References
- https://lists.debian.org/debian-lts-announce/2018/02/msg00010.html
- http://lists.unbit.it/pipermail/uwsgi/2018-February/008835.html
- https://github.com/unbit/uwsgi/commit/cb4636f7c0af2e97a4eef7a3cdcbd85a71247bfe
