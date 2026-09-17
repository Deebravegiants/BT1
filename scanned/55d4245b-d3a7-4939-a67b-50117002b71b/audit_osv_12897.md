# [H] CVE-2018-16132

## Summary
Severity: High
Advisory: CVE-2018-16132
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-16132
Type: osv

## Details
The image rendering component (createGenericPreview) of the Open Whisper Signal app through 2.29.0 for iOS fails to check for unreasonably large images before manipulating received images. This allows for a large image sent to a user to exhaust all available memory when the image is displayed, resulting in a forced restart of the device.

## References
- http://seclists.org/bugtraq/2018/Aug/57
