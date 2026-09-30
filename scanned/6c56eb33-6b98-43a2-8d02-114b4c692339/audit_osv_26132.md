# [C] Atril's CBT comic book parsing vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2023-51698
Aliases: GHSA-34rr-j8v9-v4p2
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2023-51698
Type: osv

## Details
Atril is a simple multi-page document viewer. Atril is vulnerable to a critical Command Injection Vulnerability. This vulnerability gives the attacker immediate access to the target system when the target user opens a crafted document or clicks on a crafted link/URL using a maliciously crafted CBT document which is a TAR archive. A patch is available at commit ce41df6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OT3UIQOSZ6UNH5QTFOOY2DJ4MITM2C2C/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OZKXNZ3HGH6KH65OEKVCEAOZJWNZ32FQ/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51698.json
- https://github.com/mate-desktop/atril/security/advisories/GHSA-34rr-j8v9-v4p2
- https://nvd.nist.gov/vuln/detail/CVE-2023-51698
- https://github.com/mate-desktop/atril/commit/ce41df6467521ff9fd4f16514ae7d6ebb62eb1ed
