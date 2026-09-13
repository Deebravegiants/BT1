# [M] CVE-2026-35414

## Summary
Severity: Medium
Advisory: CVE-2026-35414
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-35414
Type: osv

## Details
OpenSSH before 10.3 mishandles the authorized_keys principals option in uncommon scenarios involving a principals list in conjunction with a Certificate Authority that makes certain use of comma characters.

## References
- https://marc.info/?l=openssh-unix-dev&m=177513443901484&w=2
- https://www.openssh.org/releasenotes.html#10.3p1
- https://www.openwall.com/lists/oss-security/2026/04/02/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35414.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35414
