# [H] CVE-2016-10712

## Summary
Severity: High
Advisory: CVE-2016-10712
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2016-10712
Type: osv

## Details
In PHP before 5.5.32, 5.6.x before 5.6.18, and 7.x before 7.0.3, all of the return values of stream_get_meta_data can be controlled if the input can be controlled (e.g., during file uploads). For example, a "$uri = stream_get_meta_data(fopen($file, "r"))['uri']" call mishandles the case where $file is data:text/plain;uri=eviluri, -- in other words, metadata can be set by an attacker.

## References
- https://git.php.net/?p=php-src.git%3Ba=commit%3Bh=6297a117d77fa3a0df2e21ca926a92c231819cd5
- https://usn.ubuntu.com/3566-2/
- https://usn.ubuntu.com/3600-1/
- https://bugs.php.net/bug.php?id=71323
