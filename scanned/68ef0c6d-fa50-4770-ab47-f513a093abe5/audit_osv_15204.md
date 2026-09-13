# [H] CVE-2019-14459

## Summary
Severity: High
Advisory: CVE-2019-14459
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-31
Source: https://osv.dev/vulnerability/CVE-2019-14459
Type: osv

## Details
nfdump 1.6.17 and earlier is affected by an integer overflow in the function Process_ipfix_template_withdraw in ipfix.c that can be abused in order to crash the process remotely (denial of service).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ULSZMKA7P7REJMANVL7D6WMZ2L7IRSET/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTONOGJU5FSMFNRCT6OHXYUMDRKH4RPA/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00021.html
- https://security.gentoo.org/glsa/202003-17
- https://github.com/phaag/nfdump/commit/3b006ededaf351f1723aea6c727c9edd1b1fff9b
- https://github.com/phaag/nfdump/issues/171
