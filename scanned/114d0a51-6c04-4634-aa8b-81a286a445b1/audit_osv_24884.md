# [M] CVE-2023-2804

## Summary
Severity: Medium
Advisory: CVE-2023-2804
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-25
Source: https://osv.dev/vulnerability/CVE-2023-2804
Type: osv

## Details
A heap-based buffer overflow issue was discovered in libjpeg-turbo in h2v2_merged_upsample_internal() function of jdmrgext.c file. The vulnerability can only be exploited with 12-bit data precision for which the range of the sample data type exceeds the valid sample range, hence, an attacker could craft a 12-bit lossless JPEG image that contains out-of-range 12-bit samples. An application attempting to decompress such image using merged upsampling would lead to segmentation fault or buffer overflows, causing an application to crash.

## References
- https://access.redhat.com/security/cve/CVE-2023-2804
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2804.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2804
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-01006.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2208447
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/668#issuecomment-1492586118
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/675
- https://github.com/libjpeg-turbo/libjpeg-turbo/commit/9f756bc67a84d4566bf74a0c2432aa55da404021
