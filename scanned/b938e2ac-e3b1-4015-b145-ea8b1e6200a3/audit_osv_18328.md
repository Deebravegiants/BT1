# [M] CVE-2020-26208

## Summary
Severity: Medium
Advisory: CVE-2020-26208
Aliases: GHSA-7pr6-xq4f-qhgc
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2022-02-02
Source: https://osv.dev/vulnerability/CVE-2020-26208
Type: osv

## Details
JHEAD is a simple command line tool for displaying and some manipulation of EXIF header data embedded in Jpeg images from digital cameras. In affected versions there is a heap-buffer-overflow on jhead-3.04/jpgfile.c:285 ReadJpegSections. Crafted jpeg images can be provided to the user resulting in a program crash or potentially incorrect exif information retrieval. Users are advised to upgrade. There is no known workaround for this issue.

## References
- https://github.com/F-ZhaoYang/jhead/commit/5186ddcf9e35a7aa0ff0539489a930434a1325f4
- https://github.com/Matthias-Wandel/jhead/issues/7
- https://bugs.launchpad.net/ubuntu/+source/jhead/+bug/1900821
- https://github.com/F-ZhaoYang/jhead/security/advisories/GHSA-7pr6-xq4f-qhgc
