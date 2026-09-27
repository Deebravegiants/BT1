# [H] CVE-2021-23191

## Summary
Severity: High
Advisory: CVE-2021-23191
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-03-02
Source: https://osv.dev/vulnerability/CVE-2021-23191
Type: osv

## Details
A security issue was found in htmldoc v1.9.12 and before. A NULL pointer dereference in the function image_load_jpeg() in image.cxx may result in denial of service.

## References
- https://ubuntu.com/security/CVE-2021-23191
- https://github.com/michaelrsweet/htmldoc/issues/415
- https://bugzilla.redhat.com/show_bug.cgi?id=1967022
- https://github.com/michaelrsweet/htmldoc/commit/369b2ea1fd0d0537ba707f20a2f047b6afd2fbdc
