# [M] CVE-2019-11323

## Summary
Severity: Medium
Advisory: CVE-2019-11323
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2019-11323
Type: osv

## Details
HAProxy before 1.9.7 mishandles a reload with rotated keys, which triggers use of uninitialized, and very predictable, HMAC keys. This is related to an include/types/ssl_sock.h error.

## References
- http://git.haproxy.org/?p=haproxy.git%3Ba=commit%3Bh=8ef706502aa2000531d36e4ac56dbdc7c30f718d
- https://www.mail-archive.com/haproxy%40formilux.org/msg33410.html
