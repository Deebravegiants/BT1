# [H] CVE-2019-12185

## Summary
Severity: High
Advisory: CVE-2019-12185
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-20
Source: https://osv.dev/vulnerability/CVE-2019-12185
Type: osv

## Details
eLabFTW 1.8.5 is vulnerable to arbitrary file uploads via the /app/controllers/EntityController.php component. This may result in remote command execution. An attacker can use a user account to fully compromise the system using a POST request. This will allow for PHP files to be written to the web root, and for code to execute on the remote server.

## References
- http://incidentsecurity.com/elabftw-1-8-5-entitycontroller-arbitrary-file-upload-rce/
- https://github.com/fuzzlove/eLabFTW-1.8.5-EntityController-Arbitrary-File-Upload-RCE
