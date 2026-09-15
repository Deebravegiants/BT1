# [H] CVE-2020-27387

## Summary
Severity: High
Advisory: CVE-2020-27387
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-05
Source: https://osv.dev/vulnerability/CVE-2020-27387
Type: osv

## Details
An unrestricted file upload issue in HorizontCMS through 1.0.0-beta allows an authenticated remote attacker (with access to the FileManager) to upload and execute arbitrary PHP code by uploading a PHP payload, and then using the FileManager's rename function to provide the payload (which will receive a random name on the server) with the PHP extension, and finally executing the PHP file via an HTTP GET request to /storage/<php_file_name>. NOTE: the vendor has patched this while leaving the version number at 1.0.0-beta.

## References
- https://github.com/rapid7/metasploit-framework/pull/14340
- https://blog.vonahi.io/whats-in-a-re-name/
- https://github.com/ttimot24/HorizontCMS/commit/436b5ab679fd27afa3d99c023dbe103113da4fee
- http://packetstormsecurity.com/files/160046/HorizontCMS-1.0.0-beta-Shell-Upload.html
