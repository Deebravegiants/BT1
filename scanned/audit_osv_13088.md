# [H] CVE-2018-17336

## Summary
Severity: High
Advisory: CVE-2018-17336
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-22
Source: https://osv.dev/vulnerability/CVE-2018-17336
Type: osv

## Details
UDisks 2.8.0 has a format string vulnerability in udisks_log in udiskslogging.c, allowing attackers to obtain sensitive information (stack contents), cause a denial of service (memory corruption), or possibly have unspecified other impact via a malformed filesystem label, as demonstrated by %d or %n substrings.

## References
- https://access.redhat.com/errata/RHSA-2019:2178
- https://usn.ubuntu.com/3772-1/
- https://github.com/storaged-project/udisks/issues/578
