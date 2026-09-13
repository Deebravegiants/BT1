# [H] CVE-2018-1000839

## Summary
Severity: High
Advisory: CVE-2018-1000839
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000839
Type: osv

## Details
LH-EHR version REL-2_0_0 contains a Arbitrary File Upload vulnerability in Profile picture upload that can result in Remote Code Execution. This attack appear to be exploitable via Uploading a PHP file with image MIME type.

## References
- https://0dd.zone/2018/09/03/lh-ehr-RCE-via-picture-upload/
- https://github.com/LibreHealthIO/lh-ehr/issues/1223
