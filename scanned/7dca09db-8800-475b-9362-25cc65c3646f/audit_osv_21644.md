# [H] CVE-2021-44731

## Summary
Severity: High
Advisory: CVE-2021-44731
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-17
Source: https://osv.dev/vulnerability/CVE-2021-44731
Type: osv

## Details
A race condition existed in the snapd 2.54.2 snap-confine binary when preparing a private mount namespace for a snap. This could allow a local attacker to gain root privileges by bind-mounting their own contents inside the snap's private mount namespace and causing snap-confine to execute arbitrary code and hence gain privilege escalation. Fixed in snapd versions 2.54.3+18.04, 2.54.3+20.04 and 2.54.3+21.10.1

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3QTBN7LLZISXIA4KU4UKDR27Q5PXDS2U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XCGHG6LJAVJJ72TMART6A7N4Z6MSTGI7/
- http://www.openwall.com/lists/oss-security/2022/02/18/2
- http://www.openwall.com/lists/oss-security/2022/02/23/2
- https://www.debian.org/security/2022/dsa-5080
- https://ubuntu.com/security/notices/USN-5292-1
- http://packetstormsecurity.com/files/170176/snap-confine-must_mkdir_and_open_with_perms-Race-Condition.html
- http://seclists.org/fulldisclosure/2022/Dec/4
- http://www.openwall.com/lists/oss-security/2022/02/23/1
- http://www.openwall.com/lists/oss-security/2022/11/30/2
