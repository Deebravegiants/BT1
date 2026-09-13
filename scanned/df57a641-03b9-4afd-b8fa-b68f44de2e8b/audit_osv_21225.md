# [H] CVE-2021-4120

## Summary
Severity: High
Advisory: CVE-2021-4120
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-17
Source: https://osv.dev/vulnerability/CVE-2021-4120
Type: osv

## Details
snapd 2.54.2 fails to perform sufficient validation of snap content interface and layout paths, resulting in the ability for snaps to inject arbitrary AppArmor policy rules via malformed content interface and layout declarations and hence escape strict snap confinement. Fixed in snapd versions 2.54.3+18.04, 2.54.3+20.04 and 2.54.3+21.10.1

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QTBN7LLZISXIA4KU4UKDR27Q5PXDS2U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XCGHG6LJAVJJ72TMART6A7N4Z6MSTGI7/
- https://bugs.launchpad.net/snapd/+bug/1949368
- https://ubuntu.com/security/notices/USN-5292-1
- http://www.openwall.com/lists/oss-security/2022/02/18/2
