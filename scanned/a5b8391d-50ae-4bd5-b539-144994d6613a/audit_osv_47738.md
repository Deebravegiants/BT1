# [H] CVE-2017-11110

## Summary
Severity: High
Advisory: CVE-2017-11110
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-08
Source: https://osv.dev/vulnerability/CVE-2017-11110
Type: osv

## Details
The ole_init function in ole.c in catdoc 0.95 allows remote attackers to cause a denial of service (heap-based buffer underflow and application crash) or possibly have unspecified other impact via a crafted file, i.e., data is written to memory addresses before the beginning of the tmpBuf buffer.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1468471
