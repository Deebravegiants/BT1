# [M] CVE-2017-12145

## Summary
Severity: Medium
Advisory: CVE-2017-12145
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-12145
Type: osv

## Details
In libquicktime 1.2.4, an allocation failure was found in the function quicktime_read_ftyp in ftyp.c, which allows attackers to cause a denial of service via a crafted file.

## References
- https://somevulnsofadlab.blogspot.com/2017/07/libquicktimeallocation-failed-in_30.html
- https://sourceforge.net/p/libquicktime/mailman/message/35888849/
