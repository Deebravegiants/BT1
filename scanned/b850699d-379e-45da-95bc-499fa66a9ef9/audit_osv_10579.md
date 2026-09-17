# [M] CVE-2017-17455

## Summary
Severity: Medium
Advisory: CVE-2017-17455
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-02-20
Source: https://osv.dev/vulnerability/CVE-2017-17455
Type: osv

## Details
Mahara 16.10 before 16.10.7, 17.04 before 17.04.5, and 17.10 before 17.10.2 are vulnerable to being forced, via a man-in-the-middle attack, to interact with Mahara on the HTTP protocol rather than HTTPS even when an SSL certificate is present.

## References
- https://bugs.launchpad.net/mahara/+bug/1734767
- https://mahara.org/interaction/forum/topic.php?id=8150
- https://reviews.mahara.org/#/c/8312/
