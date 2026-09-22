# [C] Group-Office is vulnerable to RCE due to Command Injection via TNEF Attachment Handler

## Summary
Severity: Critical
Advisory: CVE-2026-25512
Aliases: GHSA-579w-jvg7-frr4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25512
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Prior to versions 6.8.150, 25.0.82, and 26.0.5, there is a remote code execution (RCE) vulnerability in Group-Office. The endpoint email/message/tnefAttachmentFromTempFile directly concatenates the user-controlled parameter tmp_file into an exec() call. By injecting shell metacharacters into tmp_file, an authenticated attacker can execute arbitrary system commands on the server. This issue has been patched in versions 6.8.150, 25.0.82, and 26.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25512.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-579w-jvg7-frr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-25512
- http://github.com/Intermesh/groupoffice/commit/6c612deca97a6cd2a1bd4feea0ce7e8e9d907792
