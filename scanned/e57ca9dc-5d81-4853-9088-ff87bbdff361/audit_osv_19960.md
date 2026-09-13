# [C] CVE-2021-28428

## Summary
Severity: Critical
Advisory: CVE-2021-28428
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-05
Source: https://osv.dev/vulnerability/CVE-2021-28428
Type: osv

## Details
File upload vulnerability in HorizontCMS before 1.0.0-beta.3 via uploading a .htaccess and *.hello files using the Media Files upload functionality. The original file upload vulnerability (CVE-2020-27387) was remediated by restricting the PHP extensions; however, we confirmed that the filter was bypassed via uploading an arbitrary .htaccess and *.hello files in order to execute PHP code to gain RCE.

## References
- https://github.com/ttimot24/HorizontCMS/commit/9c4d6827cbe96decec6834d53660e14ab2bf8838
- https://github.com/ttimot24/HorizontCMS
