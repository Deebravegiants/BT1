# [C] CVE-2023-40890

## Summary
Severity: Critical
Advisory: CVE-2023-40890
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-29
Source: https://osv.dev/vulnerability/CVE-2023-40890
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the lookup_sequence function of ZBar 0.23.90. Specially crafted QR codes may lead to information disclosure and/or arbitrary code execution. To trigger this vulnerability, an attacker can digitally input the malicious QR code, or prepare it to be physically scanned by the vulnerable scanner.

## References
- https://hackmd.io/%40cspl/H1PxPAUnn
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DC7V5YCLCPB36J2KY6WLZCABFLBRB665/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40890.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/25LZZQJGGZRPLKTRNRNOTAFQJIPS7WRP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DC7V5YCLCPB36J2KY6WLZCABFLBRB665/
- https://nvd.nist.gov/vuln/detail/CVE-2023-40890
- https://lists.debian.org/debian-lts-announce/2023/12/msg00001.html
