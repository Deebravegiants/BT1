# [H] CVE-2021-44730

## Summary
Severity: High
Advisory: CVE-2021-44730
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-17
Source: https://osv.dev/vulnerability/CVE-2021-44730
Type: osv

## Details
snapd 2.54.2 did not properly validate the location of the snap-confine binary. A local attacker who can hardlink this binary to another location to cause snap-confine to execute other arbitrary binaries and hence gain privilege escalation. Fixed in snapd versions 2.54.3+18.04, 2.54.3+20.04 and 2.54.3+21.10.1

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QTBN7LLZISXIA4KU4UKDR27Q5PXDS2U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XCGHG6LJAVJJ72TMART6A7N4Z6MSTGI7/
- http://www.openwall.com/lists/oss-security/2022/02/18/2
- http://www.openwall.com/lists/oss-security/2022/02/23/1
- https://www.debian.org/security/2022/dsa-5080
- https://ubuntu.com/security/notices/USN-5292-1
