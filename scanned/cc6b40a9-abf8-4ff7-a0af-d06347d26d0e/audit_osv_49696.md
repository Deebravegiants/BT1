# [M] CVE-2019-16275

## Summary
Severity: Medium
Advisory: CVE-2019-16275
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-12
Source: https://osv.dev/vulnerability/CVE-2019-16275
Type: osv

## Details
hostapd before 2.10 and wpa_supplicant before 2.10 allow an incorrect indication of disconnection in certain situations because source address validation is mishandled. This is a denial of service that should have been prevented by PMF (aka management frame protection). The attacker must send a crafted 802.11 frame from a location that is within the 802.11 communications range.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FEGITWRTIWABW54ANEPCEF4ARZLXGSK5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HY6STGJIIROVNIU6VMB2WTN2Q5M65WF4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36G4XAZ644DMHBLKOL4FDSPZVIGNQY6U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PBJXUKV6XMSELWNXPS37CSUIH5EUHFXQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/B7NCLOPTZNRRNYODH22BFIDH6YIQWLJD/
- https://seclists.org/bugtraq/2019/Sep/56
- https://usn.ubuntu.com/4136-2/
- https://w1.fi/security/2019-7/ap-mode-pmf-disconnection-protection-bypass.txt
- https://www.debian.org/security/2019/dsa-4538
- http://www.openwall.com/lists/oss-security/2019/09/12/6
- https://usn.ubuntu.com/4136-1/
- https://www.openwall.com/lists/oss-security/2019/09/11/7
- https://lists.debian.org/debian-lts-announce/2019/09/msg00017.html
- https://w1.fi/security/2019-7/
