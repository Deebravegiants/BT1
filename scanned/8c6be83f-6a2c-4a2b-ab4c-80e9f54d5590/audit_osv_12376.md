# [H] CVE-2018-11556

## Summary
Severity: High
Advisory: CVE-2018-11556
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-30
Source: https://osv.dev/vulnerability/CVE-2018-11556
Type: osv

## Details
tificc in Little CMS 2.9 has an out-of-bounds write in the cmsPipelineCheckAndRetreiveStages function in cmslut.c in liblcms2.a via a crafted TIFF file. NOTE: Little CMS developers do consider this a vulnerability because the issue is based on an sample program using LIBTIFF and do not apply to the lcms2 library, lcms2 does not depends on LIBTIFF other than to build sample programs, and the issue cannot be reproduced on the lcms2 library.”

## References
- https://github.com/mm2/Little-CMS/issues/167
- https://github.com/xiaoqx/pocs/tree/master/cms
