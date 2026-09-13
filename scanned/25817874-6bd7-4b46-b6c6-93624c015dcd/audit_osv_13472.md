# [C] CVE-2018-1999019

## Summary
Severity: Critical
Advisory: CVE-2018-1999019
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999019
Type: osv

## Details
Chamilo LMS version 11.x contains an Unserialization vulnerability in the "hash" GET parameter for the api endpoint located at /webservices/api/v2.php that can result in Unauthenticated remote code execution. This attack appear to be exploitable via a simple GET request to the api endpoint. This vulnerability appears to have been fixed in After commit 0de84700648f098c1fbf6b807dee28ec640efe62.

## References
- https://ibb.co/jBxe6y
- https://github.com/chamilo/chamilo-lms/commit/0de84700648f098c1fbf6b807dee28ec640efe62
