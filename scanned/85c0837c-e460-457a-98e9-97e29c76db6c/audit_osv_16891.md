# [C] CVE-2020-10567

## Summary
Severity: Critical
Advisory: CVE-2020-10567
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-14
Source: https://osv.dev/vulnerability/CVE-2020-10567
Type: osv

## Details
An issue was discovered in Responsive Filemanager through 9.14.0. In the ajax_calls.php file in the save_img action in the name parameter, there is no validation of what kind of extension is sent. This makes it possible to execute PHP code if a legitimate JPEG image contains this code in the EXIF data, and the .php extension is used in the name parameter. (A potential fast patch is to disable the save_img action in the config file.)

## References
- http://packetstormsecurity.com/files/171280/ZwiiCMS-12.2.04-Remote-Code-Execution.html
- https://github.com/trippo/ResponsiveFilemanager/issues/600
