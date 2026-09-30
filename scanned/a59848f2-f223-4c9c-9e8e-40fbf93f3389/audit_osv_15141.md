# [M] CVE-2019-13960

## Summary
Severity: Medium
Advisory: CVE-2019-13960
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-13960
Type: osv

## Details
In libjpeg-turbo 2.0.2, a large amount of memory can be used during processing of an invalid progressive JPEG image containing incorrect width and height values in the image header. NOTE: the vendor's expectation, for use cases in which this memory usage would be a denial of service, is that the application should interpret libjpeg warnings as fatal errors (aborting decompression) and/or set limits on resource consumption or image sizes

## References
- https://libjpeg-turbo.org/pmwiki/uploads/About/TwoIssueswiththeJPEGStandard.pdf
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/337
