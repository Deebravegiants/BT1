# [H] CVE-2020-25648

## Summary
Severity: High
Advisory: CVE-2020-25648
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-20
Source: https://osv.dev/vulnerability/CVE-2020-25648
Type: osv

## Details
A flaw was found in the way NSS handled CCS (ChangeCipherSpec) messages in TLS 1.3. This flaw allows a remote attacker to send multiple CCS messages, causing a denial of service for servers compiled with the NSS library. The highest threat from this vulnerability is to system availability. This flaw affects NSS versions before 3.58.

## References
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2023/10/msg00039.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRM53IQCPZT2US3M7JXTP6I6IBA5RGOD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ERA5SVJQXQMDGES7RIT4F4NQVLD35RXN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RPOLN6DJUYQ3QBQEGLZGV73SNIPK7GHV/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSS/NSS_3.58_release_notes
- https://bugzilla.redhat.com/show_bug.cgi?id=1887319
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
