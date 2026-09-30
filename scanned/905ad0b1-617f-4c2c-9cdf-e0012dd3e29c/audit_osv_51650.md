# [M] CVE-2021-37746

## Summary
Severity: Medium
Advisory: CVE-2021-37746
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-07-30
Source: https://osv.dev/vulnerability/CVE-2021-37746
Type: osv

## Details
textview_uri_security_check in textview.c in Claws Mail before 3.18.0, and Sylpheed through 3.7.0, does not have sufficient link checks before accepting a click.

## References
- https://git.claws-mail.org/?p=claws.git%3Ba=commit%3Bh=ac286a71ed78429e16c612161251b9ea90ccd431
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L2QNUIWASJLPUZZKWICGCEGYJZCQE7NH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RCJXHUSYHGVBSH2ULD7HNXLM7QNRECZ6/
- https://claws-mail.org/download.php?file=releases/claws-mail-3.18.0.tar.xz
- https://sylpheed.sraoss.jp/sylpheed/v3.7/sylpheed-3.7.0.tar.xz
