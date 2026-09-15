# [H] CVE-2023-34059

## Summary
Severity: High
Advisory: CVE-2023-34059
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-27
Source: https://osv.dev/vulnerability/CVE-2023-34059
Type: osv

## Details
open-vm-tools contains a file descriptor hijack vulnerability in the vmware-user-suid-wrapper. A malicious actor with non-root privileges may be able to hijack the 
/dev/uinput file descriptor allowing them to simulate user inputs.

## References
- http://www.openwall.com/lists/oss-security/2023/10/27/2
- http://www.openwall.com/lists/oss-security/2023/10/27/3
- http://www.openwall.com/lists/oss-security/2023/11/26/1
- http://www.openwall.com/lists/oss-security/2023/11/27/1
- https://lists.debian.org/debian-lts-announce/2023/11/msg00002.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G7G77Z76CQPGUF7VHRA6O3UFCMPPR4O2/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MQUOFQL2SNNNMKROQ3TZQY4HEYMNOIBW/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WLTKVTRKQW2GD2274H3UOW6XU4E62GSK/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34059.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34059
- https://www.debian.org/security/2023/dsa-5543
- https://www.vmware.com/security/advisories/VMSA-2023-0024.html
- https://www.openwall.com/lists/oss-security/2023/10/27/3
