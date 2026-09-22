# [H] GSS-NTLMSSP vulnerable to memory leak when parsing usernames

## Summary
Severity: High
Advisory: CVE-2023-25566
Aliases: GHSA-mfm4-6g58-jw74
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-25566
Type: osv

## Details
GSS-NTLMSSP is a mechglue plugin for the GSSAPI library that implements NTLM authentication. Prior to version 1.2.0, a memory leak can be triggered when parsing usernames which can trigger a denial-of-service. The domain portion of a username may be overridden causing an allocated memory area the size of the domain name to be leaked. An attacker can leak memory via the main `gss_accept_sec_context` entry point, potentially causing a denial-of-service. This issue is fixed in version 1.2.0.

## References
- https://github.com/gssapi/gss-ntlmssp/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25566.json
- https://github.com/gssapi/gss-ntlmssp/security/advisories/GHSA-mfm4-6g58-jw74
- https://nvd.nist.gov/vuln/detail/CVE-2023-25566
- https://github.com/gssapi/gss-ntlmssp/commit/8660fb16474054e692a596e9c79670cd4d3954f4
