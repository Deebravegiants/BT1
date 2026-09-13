# [M] GSS-NTLMSSP vulnerable to memory corruption when decoding UTF16 strings

## Summary
Severity: Medium
Advisory: CVE-2023-25564
Aliases: GHSA-r85x-q5px-9xfq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-25564
Type: osv

## Details
GSS-NTLMSSP is a mechglue plugin for the GSSAPI library that implements NTLM authentication. Prior to version 1.2.0, memory corruption can be triggered when decoding UTF16 strings. The variable `outlen` was not initialized and could cause writing a zero to an arbitrary place in memory if `ntlm_str_convert()` were to fail, which would leave `outlen` uninitialized. This can lead to a denial of service if the write hits unmapped memory or randomly corrupts a byte in the application memory space. This vulnerability can trigger an out-of-bounds write, leading to memory corruption. This vulnerability can be triggered via the main `gss_accept_sec_context` entry point. This issue is fixed in version 1.2.0.

## References
- https://github.com/gssapi/gss-ntlmssp/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25564.json
- https://github.com/gssapi/gss-ntlmssp/security/advisories/GHSA-r85x-q5px-9xfq
- https://nvd.nist.gov/vuln/detail/CVE-2023-25564
- https://github.com/gssapi/gss-ntlmssp/commit/c753000eb31835c0664e528fbc99378ae0cbe950
