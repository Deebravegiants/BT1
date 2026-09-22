# [H] CVE-2016-7044

## Summary
Severity: High
Advisory: CVE-2016-7044
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-27
Source: https://osv.dev/vulnerability/CVE-2016-7044
Type: osv

## Details
The unformat_24bit_color function in the format parsing code in Irssi before 0.8.20, when compiled with true-color enabled, allows remote attackers to cause a denial of service (heap corruption and crash) via an incomplete 24bit color code.

## References
- http://www.securitytracker.com/id/1036868
- http://www.debian.org/security/2016/dsa-3672
- http://www.ubuntu.com/usn/USN-3086-1
- https://irssi.org/security/irssi_sa_2016.txt
