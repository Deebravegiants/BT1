# [C] CVE-2018-10685

## Summary
Severity: Critical
Advisory: CVE-2018-10685
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2018-10685
Type: osv

## Details
In Long Range Zip (aka lrzip) 0.631, there is a use-after-free in the lzma_decompress_buf function of stream.c, which allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact.

## References
- https://lists.debian.org/debian-lts-announce/2021/08/msg00001.html
- https://github.com/ckolivas/lrzip/issues/95
