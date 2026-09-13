# [C] CVE-2017-5946

## Summary
Severity: Critical
Advisory: CVE-2017-5946
Aliases: GHSA-gcqq-w6gr-h9j9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/CVE-2017-5946
Type: osv

## Details
The Zip::File component in the rubyzip gem before 1.2.1 for Ruby has a directory traversal vulnerability. If a site allows uploading of .zip files, an attacker can upload a malicious file that uses "../" pathname substrings to write arbitrary files to the filesystem.

## References
- http://www.debian.org/security/2017/dsa-3801
- http://www.securityfocus.com/bid/96445
- https://github.com/rubyzip/rubyzip/issues/315
- https://github.com/rubyzip/rubyzip/releases
