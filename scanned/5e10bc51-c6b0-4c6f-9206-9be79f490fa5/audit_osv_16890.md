# [H] CVE-2020-10557

## Summary
Severity: High
Advisory: CVE-2020-10557
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/CVE-2020-10557
Type: osv

## Details
An issue was discovered in AContent through 1.4. It allows the user to run commands on the server with a low-privileged account. The upload section in the file manager page contains an arbitrary file upload vulnerability via upload.php. The extension .php7 bypasses file upload restrictions.

## References
- https://sourceforge.net/projects/acontent/
- https://github.com/cinzinga/CVEs/tree/master/CVE-2020-10557
