# [M] CVE-2021-22564

## Summary
Severity: Medium
Advisory: CVE-2021-22564
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-01
Source: https://osv.dev/vulnerability/CVE-2021-22564
Type: osv

## Details
For certain valid JPEG XL images with a size slightly larger than an integer number of groups (256x256 pixels) when processing the groups out of order the decoder can perform an out of bounds copy of image pixels from an image buffer in the heap to another. This copy can occur when processing the right or bottom edges of the image, but only when groups are processed in certain order. Groups can be processed out of order in multi-threaded decoding environments with heavy thread load but also with images that contain the groups in an arbitrary order in the file. It is recommended to upgrade past 0.6.0 or patch with https://github.com/libjxl/libjxl/pull/775

## References
- https://github.com/libjxl/libjxl/issues/708
- https://github.com/libjxl/libjxl/pull/775
