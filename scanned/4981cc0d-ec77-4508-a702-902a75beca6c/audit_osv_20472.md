# [H] CVE-2021-3403

## Summary
Severity: High
Advisory: CVE-2021-3403
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-04
Source: https://osv.dev/vulnerability/CVE-2021-3403
Type: osv

## Details
In ytnef 1.9.3, the TNEFSubjectHandler function in lib/ytnef.c allows remote attackers to cause a denial-of-service (and potentially code execution) due to a double free which can be triggered via a crafted file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1926967
- https://github.com/Yeraze/ytnef/issues/85
