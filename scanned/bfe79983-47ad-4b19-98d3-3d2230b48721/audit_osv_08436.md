# [M] CVE-2016-3182

## Summary
Severity: Medium
Advisory: CVE-2016-3182
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-02-20
Source: https://osv.dev/vulnerability/CVE-2016-3182
Type: osv

## Details
The color_esycc_to_rgb function in bin/common/color.c in OpenJPEG before 2.1.1 allows attackers to cause a denial of service (memory corruption) via a crafted jpeg 2000 file.

## References
- http://www.openwall.com/lists/oss-security/2016/03/16/16
- http://www.openwall.com/lists/oss-security/2016/09/27/1
- https://github.com/uclouvain/openjpeg/issues/725
- https://bugzilla.redhat.com/show_bug.cgi?id=1317826
