# [C] CVE-2017-14230

## Summary
Severity: Critical
Advisory: CVE-2017-14230
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-09-10
Source: https://osv.dev/vulnerability/CVE-2017-14230
Type: osv

## Details
In the mboxlist_do_find function in imap/mboxlist.c in Cyrus IMAP before 3.0.4, an off-by-one error in prefix calculation for the LIST command caused use of uninitialized memory, which might allow remote attackers to obtain sensitive information or cause a denial of service (daemon crash) via a 'LIST "" "Other Users"' command.

## References
- https://lists.andrew.cmu.edu/pipermail/cyrus-announce/2017-September/000145.html
- https://www.cyrusimap.org/imap/download/release-notes/3.0/x/3.0.4.html
- https://github.com/cyrusimap/cyrus-imapd/issues/2132
- https://github.com/cyrusimap/cyrus-imapd/commit/6bd33275368edfa71ae117de895488584678ac79
