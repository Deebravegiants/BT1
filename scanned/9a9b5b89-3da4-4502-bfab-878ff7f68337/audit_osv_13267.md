# [H] CVE-2018-18956

## Summary
Severity: High
Advisory: CVE-2018-18956
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-05
Source: https://osv.dev/vulnerability/CVE-2018-18956
Type: osv

## Details
The ProcessMimeEntity function in util-decode-mime.c in Suricata 4.x before 4.0.6 allows remote attackers to cause a denial of service (segfault and daemon crash) via crafted input to the SMTP parser, as exploited in the wild in November 2018.

## References
- https://lists.openinfosecfoundation.org/pipermail/oisf-users/2018-November/016316.html
- https://lists.openinfosecfoundation.org/pipermail/oisf-users/2018-October/016227.html
- https://redmine.openinfosecfoundation.org/issues/2658#change-10374
