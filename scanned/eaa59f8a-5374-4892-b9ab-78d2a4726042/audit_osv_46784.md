# [M] CVE-2015-2774

## Summary
Severity: Medium
Advisory: CVE-2015-2774
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2015-2774
Type: osv

## Details
Erlang/OTP before 18.0-rc1 does not properly check CBC padding bytes when terminating connections, which makes it easier for man-in-the-middle attackers to obtain cleartext data via a padding-oracle attack, a variant of CVE-2014-3566 (aka POODLE).

## References
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00124.html
- http://openwall.com/lists/oss-security/2015/03/27/6
- http://www.oracle.com/technetwork/topics/security/bulletinapr2015-2511959.html
- https://web.archive.org/web/20150905124006/http://www.erlang.org/news/85
- https://www.imperialviolet.org/2014/12/08/poodleagain.html
- http://openwall.com/lists/oss-security/2015/03/27/9
- http://www.securityfocus.com/bid/73398
- https://usn.ubuntu.com/3571-1/
