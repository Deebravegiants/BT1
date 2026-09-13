# [H] CVE-2005-2946

## Summary
Severity: High
Advisory: CVE-2005-2946
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2005-09-16
Source: https://osv.dev/vulnerability/CVE-2005-2946
Type: osv

## Details
The default configuration on OpenSSL before 0.9.8 uses MD5 for creating message digests instead of a more cryptographically strong algorithm, which makes it easier for remote attackers to forge certificates with a valid certificate authority signature.

## References
- http://www.ubuntu.com/usn/usn-179-1
- https://bugzilla.ubuntu.com/show_bug.cgi?id=13593
- https://bugzilla.ubuntu.com/show_bug.cgi?id=13593
- http://www.cits.rub.de/MD5Collisions/
