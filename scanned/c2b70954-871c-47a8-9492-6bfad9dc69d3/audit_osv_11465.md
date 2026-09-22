# [M] CVE-2017-7962

## Summary
Severity: Medium
Advisory: CVE-2017-7962
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-19
Source: https://osv.dev/vulnerability/CVE-2017-7962
Type: osv

## Details
The iwgif_read_image function in imagew-gif.c in libimageworsener.a in ImageWorsener 1.3.0 allows remote attackers to cause a denial of service (divide-by-zero error and application crash) via a crafted file.

## References
- https://security.gentoo.org/glsa/201706-06
- https://blogs.gentoo.org/ago/2017/04/17/imageworsener-divide-by-zero-in-iwgif_record_pixel-imagew-gif-c/
- https://github.com/jsummers/imageworsener/commit/ca3356eb49fee03e2eaf6b6aff826988c1122d93
- https://github.com/jsummers/imageworsener/issues/15
