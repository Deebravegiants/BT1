# [M] LibTIFF master branch has an out-of-bounds read in LZWDecode in `libtiff/tif_lzw.c:619`, allowing...

## Summary
Severity: Medium
Advisory: JLSEC-2025-270
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-270
Type: osv

## Affected
- Julia: `Libtiff_jll` — affected >=4.3.0+0 <4.4.0+0

## Details
LibTIFF master branch has an out-of-bounds read in LZWDecode in `libtiff/tif_lzw.c:619`, allowing attackers to cause a denial-of-service via a crafted tiff file. For users that compile libtiff from sources, the fix is available with commit b4e79bfa.

## References
- http://seclists.org/fulldisclosure/2022/Oct/28
- http://seclists.org/fulldisclosure/2022/Oct/39
- http://seclists.org/fulldisclosure/2022/Oct/41
- https://gitlab.com/gitlab-org/cves/-/blob/master/2022/CVE-2022-1622.json
- https://gitlab.com/libtiff/libtiff/-/commit/b4e79bfa0c7d2d08f6f1e7ec38143fc8cb11394a
- https://gitlab.com/libtiff/libtiff/-/issues/410
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C7IWZTB4J2N4F5OR5QY4VHDSKWKZSWN3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UXAFOP6QQRNZD3HPZ6BMCEZZOM4YIZMK/
- https://security.netapp.com/advisory/ntap-20220616-0005/
- https://support.apple.com/kb/HT213443
- https://support.apple.com/kb/HT213444
- https://support.apple.com/kb/HT213446
- https://support.apple.com/kb/HT213486
- https://support.apple.com/kb/HT213487
- https://support.apple.com/kb/HT213488
