# [M] CVE-2018-18655

## Summary
Severity: Medium
Advisory: CVE-2018-18655
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2018-10-26
Source: https://osv.dev/vulnerability/CVE-2018-18655
Type: osv

## Details
Prayer through 1.3.5 sends a Referer header, containing a user's username, when a user clicks on a link in their email because header.t lacks a no-referrer setting.

## References
- https://telescoper.wordpress.com/2018/10/18/a-breakthrough-for-a-bigot/#comment-339386
- https://bugs.debian.org/911842
