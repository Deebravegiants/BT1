# [M] GSS-NTLMSSP vulnerable to multiple out-of-bounds reads when decoding NTLM fields

## Summary
Severity: Medium
Advisory: CVE-2023-25563
Aliases: GHSA-jjjx-5qf7-9mgf
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-25563
Type: osv

## Details
GSS-NTLMSSP is a mechglue plugin for the GSSAPI library that implements NTLM authentication. Prior to version 1.2.0, multiple out-of-bounds reads when decoding NTLM fields can trigger a denial of service. A 32-bit integer overflow condition can lead to incorrect checks of consistency of length of internal buffers. Although most applications will error out before accepting a singe input buffer of 4GB in length this could theoretically happen. This vulnerability can be triggered via the main `gss_accept_sec_context` entry point if the application allows tokens greater than 4GB in length. This can lead to a large, up to 65KB, out-of-bounds read which could cause a denial-of-service if it reads from unmapped memory. Version 1.2.0 contains a patch for the out-of-bounds reads.

## References
- https://github.com/gssapi/gss-ntlmssp/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25563.json
- https://github.com/gssapi/gss-ntlmssp/security/advisories/GHSA-jjjx-5qf7-9mgf
- https://nvd.nist.gov/vuln/detail/CVE-2023-25563
- https://github.com/gssapi/gss-ntlmssp/commit/97c62c6167299028d80765080e74d91dfc99efbd
