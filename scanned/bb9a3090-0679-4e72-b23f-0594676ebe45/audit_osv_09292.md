# [H] CVE-2016-9424

## Summary
Severity: High
Advisory: CVE-2016-9424
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-12
Source: https://osv.dev/vulnerability/CVE-2016-9424
Type: osv

## Details
An issue was discovered in the Tatsuya Kinoshita w3m fork before 0.5.3-31. w3m doesn't properly validate the value of tag attribute, which allows remote attackers to cause a denial of service (heap buffer overflow crash) and possibly execute arbitrary code via a crafted HTML page.

## References
- http://www.securityfocus.com/bid/94407
- http://www.openwall.com/lists/oss-security/2016/11/18/3
- https://security.gentoo.org/glsa/201701-08
- https://github.com/tats/w3m/blob/master/ChangeLog
- https://github.com/tats/w3m/issues/12
