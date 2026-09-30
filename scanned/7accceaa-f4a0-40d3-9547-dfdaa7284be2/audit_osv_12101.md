# [H] CVE-2018-10242

## Summary
Severity: High
Advisory: CVE-2018-10242
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-04-04
Source: https://osv.dev/vulnerability/CVE-2018-10242
Type: osv

## Details
Suricata version 4.0.4 incorrectly handles the parsing of the SSH banner. A malformed SSH banner can cause the parsing code to read beyond the allocated data because SSHParseBanner in app-layer-ssh.c lacks a length check.

## References
- https://lists.debian.org/debian-lts-announce/2019/04/msg00010.html
- https://suricata-ids.org/2018/07/18/suricata-4-0-5-available/
