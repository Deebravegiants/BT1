# [H] CVE-2016-4476

## Summary
Severity: High
Advisory: CVE-2016-4476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-09
Source: https://osv.dev/vulnerability/CVE-2016-4476
Type: osv

## Details
hostapd 0.6.7 through 2.5 and wpa_supplicant 0.6.7 through 2.5 do not reject \n and \r characters in passphrase parameters, which allows remote attackers to cause a denial of service (daemon outage) via a crafted WPS operation.

## References
- http://www.openwall.com/lists/oss-security/2016/05/03/12
- http://www.ubuntu.com/usn/USN-3455-1
