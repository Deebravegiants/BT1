# [M] CVE-2015-5310

## Summary
Severity: Medium
Advisory: CVE-2015-5310
CVSS: 4.3 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-01-06
Source: https://osv.dev/vulnerability/CVE-2015-5310
Type: osv

## Details
The WNM Sleep Mode code in wpa_supplicant 2.x before 2.6 does not properly ignore key data in response frames when management frame protection (MFP) was not negotiated, which allows remote attackers to inject arbitrary broadcast or multicast packets or cause a denial of service (ignored packets) via a WNM Sleep Mode response.

## References
- http://source.android.com/security/bulletin/2016-01-01.html
- http://www.debian.org/security/2015/dsa-3397
- http://www.ubuntu.com/usn/USN-2808-1
- http://w1.fi/security/2015-6/wpa_supplicant-unauthorized-wnm-sleep-mode-gtk-control.txt
- http://www.openwall.com/lists/oss-security/2015/11/10/9
- http://www.securityfocus.com/bid/77541
- http://www.securitytracker.com/id/1034592
