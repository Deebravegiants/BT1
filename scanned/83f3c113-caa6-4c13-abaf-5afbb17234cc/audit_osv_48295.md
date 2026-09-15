# [H] CVE-2017-5836

## Summary
Severity: High
Advisory: CVE-2017-5836
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2017-5836
Type: osv

## Details
The plist_free_data function in plist.c in libplist allows attackers to cause a denial of service (crash) via vectors involving an integer node that is treated as a PLIST_KEY and then triggers an invalid free.

## References
- http://www.securityfocus.com/bid/96022
- http://www.openwall.com/lists/oss-security/2017/01/31/6
- http://www.openwall.com/lists/oss-security/2017/02/02/4
- https://github.com/libimobiledevice/libplist/issues/86
