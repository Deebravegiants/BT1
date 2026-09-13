# [H] CVE-2021-45463

## Summary
Severity: High
Advisory: CVE-2021-45463
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-45463
Type: osv

## Details
load_cache in GEGL before 0.4.34 allows shell expansion when a pathname in a constructed command line is not escaped or filtered. This is caused by use of the system library function for execution of the ImageMagick convert fallback in magick-load. NOTE: GEGL releases before 0.4.34 are used in GIMP releases before 2.10.30; however, this does not imply that GIMP builds enable the vulnerable feature.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CG635WJCNXHJM5U4BGMAAP4NK2YFTQXK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZP5NDNOTMPI335FXE7VUPW7FXYTT7PYN/
- https://gitlab.gnome.org/GNOME/gegl/-/blob/master/docs/NEWS.adoc
- https://gitlab.gnome.org/GNOME/gegl/-/issues/298
- https://www.gimp.org/news/2021/12/21/gimp-2-10-30-released/
- https://gitlab.gnome.org/GNOME/gegl/-/commit/bfce470f0f2f37968862129d5038b35429f2909b
- https://gitlab.gnome.org/GNOME/gimp/-/commit/e8a31ba4f2ce7e6bc34882dc27c97fba993f5868
