# [M] Libopensc: incorrect handling length of buffers or files in libopensc

## Summary
Severity: Medium
Advisory: CVE-2024-45619
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-45619
Type: osv

## Details
A vulnerability was found in OpenSC, OpenSC tools, PKCS#11 module, minidriver, and CTK. An attacker could use a crafted USB Device or Smart Card, which would present the system with a specially crafted response to APDUs. When buffers are partially filled with data, initialized parts of the buffer can be incorrectly accessed.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00026.html
- https://access.redhat.com/security/cve/CVE-2024-45619
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45619.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45619
- https://bugzilla.redhat.com/show_bug.cgi?id=2309288
- https://github.com/OpenSC/OpenSC
