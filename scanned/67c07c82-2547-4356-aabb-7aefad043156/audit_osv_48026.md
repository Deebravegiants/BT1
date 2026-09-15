# [M] CVE-2017-17440

## Summary
Severity: Medium
Advisory: CVE-2017-17440
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/CVE-2017-17440
Type: osv

## Details
GNU Libextractor 1.6 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted GIF, IT (Impulse Tracker), NSFE, S3M (Scream Tracker 3), SID, or XM (eXtended Module) file, as demonstrated by the EXTRACTOR_xm_extract_method function in plugins/xm_extractor.c.

## References
- http://www.securityfocus.com/bid/102116
- https://lists.gnu.org/archive/html/bug-libextractor/2017-11/msg00005.html
- https://gnunet.org/git/libextractor.git/commit/?id=7cc63b001ceaf81143795321379c835486d0c92e
- https://lists.gnu.org/archive/html/bug-libextractor/2017-11/msg00002.html
- https://lists.gnu.org/archive/html/bug-libextractor/2017-11/msg00004.html
- https://bugs.debian.org/883528#35
- https://lists.gnu.org/archive/html/bug-libextractor/2017-11/msg00000.html
- https://lists.gnu.org/archive/html/bug-libextractor/2017-11/msg00001.html
