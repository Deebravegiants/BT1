# [H] CVE-2019-16347

## Summary
Severity: High
Advisory: CVE-2019-16347
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2019-16347
Type: osv

## Details
ngiflib 0.4 has a heap-based buffer overflow in WritePixels() in ngiflib.c when called from DecodeGifImg, because deinterlacing for small pictures is mishandled.

## References
- https://github.com/miniupnp/ngiflib/issues/12
- https://github.com/miniupnp/ngiflib/commit/37d939a6f511d16d4c95678025c235fe62e6417a
