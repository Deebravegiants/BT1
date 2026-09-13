# [H] CVE-2018-10717

## Summary
Severity: High
Advisory: CVE-2018-10717
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-03
Source: https://osv.dev/vulnerability/CVE-2018-10717
Type: osv

## Details
The DecodeGifImg function in ngiflib.c in MiniUPnP ngiflib 0.4 does not consider the bounds of the pixels data structure, which allows remote attackers to cause a denial of service (WritePixels heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted GIF file, a different vulnerability than CVE-2018-10677.

## References
- https://github.com/miniupnp/ngiflib/commit/cf429e0a2fe26b5f01ce0c8e9b79432e94509b6e
- https://github.com/miniupnp/ngiflib/issues/3
