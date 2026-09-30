# [H] CVE-2017-18123

## Summary
Severity: High
Advisory: CVE-2017-18123
CVSS: 8.6 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2018-02-03
Source: https://osv.dev/vulnerability/CVE-2017-18123
Type: osv

## Details
The call parameter of /lib/exe/ajax.php in DokuWiki through 2017-02-19e does not properly encode user input, which leads to a reflected file download vulnerability, and allows remote attackers to run arbitrary programs.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00004.html
- https://github.com/splitbrain/dokuwiki/issues/2029
- https://github.com/splitbrain/dokuwiki/pull/2019
- https://hackerone.com/reports/238316
- https://lists.debian.org/debian-lts-announce/2018/02/msg00004.html
- https://github.com/splitbrain/dokuwiki/commit/238b8e878ad48f370903465192b57c2072f65d86
- https://vulnhive.com/2018/000004
