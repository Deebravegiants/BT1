# [M] CVE-2018-20430

## Summary
Severity: Medium
Advisory: CVE-2018-20430
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-24
Source: https://osv.dev/vulnerability/CVE-2018-20430
Type: osv

## Details
GNU Libextractor through 1.8 has an out-of-bounds read vulnerability in the function history_extract() in plugins/ole2_extractor.c, related to EXTRACTOR_common_convert_to_utf8 in common/convert.c.

## References
- https://gnunet.org/git/libextractor.git/tree/ChangeLog
- https://lists.debian.org/debian-lts-announce/2018/12/msg00015.html
- https://www.debian.org/security/2018/dsa-4361
- http://www.securityfocus.com/bid/106300
- https://gnunet.org/bugs/view.php?id=5493
- https://gnunet.org/git/libextractor.git/commit/?id=b405d707b36e0654900cba78e89f49779efea110
