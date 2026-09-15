# [H] CVE-2018-6360

## Summary
Severity: High
Advisory: CVE-2018-6360
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-01-28
Source: https://osv.dev/vulnerability/CVE-2018-6360
Type: osv

## Details
mpv through 0.28.0 allows remote attackers to execute arbitrary code via a crafted web site, because it reads HTML documents containing VIDEO elements, and accepts arbitrary URLs in a src attribute without a protocol whitelist in player/lua/ytdl_hook.lua. For example, an av://lavfi:ladspa=file= URL signifies that the product should call dlopen on a shared object file located at an arbitrary local pathname. The issue exists because the product does not consider that youtube-dl can provide a potentially unsafe URL.

## References
- https://security.gentoo.org/glsa/201805-05
- https://www.debian.org/security/2018/dsa-4105
- https://github.com/mpv-player/mpv/commit/e6e6b0dcc7e9b0dbf35154a179b3dc1fcfcaff43
- https://github.com/mpv-player/mpv/issues/5456
