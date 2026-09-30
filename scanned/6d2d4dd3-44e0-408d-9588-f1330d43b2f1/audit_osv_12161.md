# [H] CVE-2018-10677

## Summary
Severity: High
Advisory: CVE-2018-10677
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2018-10677
Type: osv

## Details
The DecodeGifImg function in ngiflib.c in MiniUPnP ngiflib 0.4 lacks certain checks against width and height, which allows remote attackers to cause a denial of service (WritePixels heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted GIF file.

## References
- https://github.com/miniupnp/ngiflib/commit/b588a2249c7abbfc52173e32ee11d6facef82f89
- https://github.com/miniupnp/ngiflib/issues/1
