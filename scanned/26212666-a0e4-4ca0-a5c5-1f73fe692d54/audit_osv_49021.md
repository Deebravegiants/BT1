# [M] CVE-2018-20453

## Summary
Severity: Medium
Advisory: CVE-2018-20453
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-25
Source: https://osv.dev/vulnerability/CVE-2018-20453
Type: osv

## Details
The getlong function in numutils.c in libdoc through 2017-10-23 has a heap-based buffer over-read that allows attackers to cause a denial of service (application crash) via a crafted file.

## References
- https://github.com/uvoteam/libdoc/issues/1
