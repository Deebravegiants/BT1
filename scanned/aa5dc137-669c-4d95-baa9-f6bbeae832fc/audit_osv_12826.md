# [M] CVE-2018-15378

## Summary
Severity: Medium
Advisory: CVE-2018-15378
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/CVE-2018-15378
Type: osv

## Details
A vulnerability in ClamAV versions prior to 0.100.2 could allow an attacker to cause a denial of service (DoS) condition. The vulnerability is due to an error related to the MEW unpacker within the "unmew11()" function (libclamav/mew.c), which can be exploited to trigger an invalid read memory access via a specially crafted EXE file.

## References
- https://lists.debian.org/debian-lts-announce/2018/10/msg00014.html
- https://security.gentoo.org/glsa/201904-12
- https://usn.ubuntu.com/3789-1/
- https://usn.ubuntu.com/3789-2/
- https://www.flexera.com/company/secunia-research/advisories/SR-2018-23.html
- https://secuniaresearch.flexerasoftware.com/advisories/83000/
- https://bugzilla.clamav.net/show_bug.cgi?id=12170
