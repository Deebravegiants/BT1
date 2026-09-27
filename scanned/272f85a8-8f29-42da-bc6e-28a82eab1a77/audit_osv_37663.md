# [H] Git for Windows: `git clone` from manipulated repositories can leak NTLM hashes to arbitrary servers

## Summary
Severity: High
Advisory: CVE-2026-32631
Aliases: GHSA-9j5h-h4m7-85hx
CVSS: 7.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/CVE-2026-32631
Type: osv

## Details
Git for Windows is the Windows port of Git. Versions prior to 2.53.0.windows.3 do not have protections that prevent attackers from obtaining a user's NTLM hash. The NTLM hash can be obtained by tricking users into cloning a malicious repository, or checking out a malicious branch, that accesses an attacker-controlled server. By default, NTLM authentication does not need any user interaction. By brute-forcing the NTLMv2 hash (which is expensive, but possible), credentials can be extracted. This issue has been fixed in version 2.53.0.windows.3.

## References
- https://github.com/git-for-windows/git/releases/tag/v2.53.0.windows.3
- https://learn.microsoft.com/en-au/windows/whats-new/deprecated-features#:~:text=NTLM
- https://support.microsoft.com/en-us/topic/upcoming-changes-to-ntlmv1-in-windows-11-version-24h2-and-windows-server-2025-c0554217-cdbc-420f-b47c-e02b2db49b2e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32631.json
- https://github.com/git-for-windows/git/security/advisories/GHSA-9j5h-h4m7-85hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-32631
- https://techcommunity.microsoft.com/blog/windows-itpro-blog/the-evolution-of-windows-authentication/3926848
