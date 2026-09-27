# [H] CVE-2018-20483

## Summary
Severity: High
Advisory: CVE-2018-20483
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-26
Source: https://osv.dev/vulnerability/CVE-2018-20483
Type: osv

## Details
set_file_metadata in xattr.c in GNU Wget before 1.20.1 stores a file's origin URL in the user.xdg.origin.url metadata attribute of the extended attributes of the downloaded file, which allows local users to obtain sensitive information (e.g., credentials contained in the URL) by reading this attribute, as demonstrated by getfattr. This also applies to Referer information in the user.xdg.referrer.url metadata attribute. According to 2016-07-22 in the Wget ChangeLog, user.xdg.origin.url was partially based on the behavior of fwrite_xattr in tool_xattr.c in curl.

## References
- https://usn.ubuntu.com/3943-1/
- http://www.securityfocus.com/bid/106358
- https://access.redhat.com/errata/RHSA-2019:3701
- https://security.gentoo.org/glsa/201903-08
- https://security.netapp.com/advisory/ntap-20190321-0002/
- http://git.savannah.gnu.org/cgit/wget.git/tree/NEWS
- https://twitter.com/marcan42/status/1077676739877232640
