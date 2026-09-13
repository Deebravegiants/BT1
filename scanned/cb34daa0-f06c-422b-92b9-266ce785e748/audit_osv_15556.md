# [H] CVE-2019-17188

## Summary
Severity: High
Advisory: CVE-2019-17188
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-04
Source: https://osv.dev/vulnerability/CVE-2019-17188
Type: osv

## Details
An unrestricted file upload vulnerability was discovered in catalog/productinfo/imageupload in Fecshop FecMall 2.3.4. An attacker can bypass a front-end restriction and upload PHP code to the webserver, by providing image data and the image/jpeg content type, with a .php extension. This occurs because the code relies on the getimagesize function.

## References
- https://github.com/fecshop/yii2_fecshop/issues/77
