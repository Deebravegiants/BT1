# [H] GSS-NTLMSSP vulnerable to out-of-bounds read when decoding target information

## Summary
Severity: High
Advisory: CVE-2023-25567
Aliases: GHSA-24pf-6prf-24ch
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-25567
Type: osv

## Details
GSS-NTLMSSP, a mechglue plugin for the GSSAPI library that implements NTLM authentication, has an out-of-bounds read when decoding target information prior to version 1.2.0. The length of the `av_pair` is not checked properly for two of the elements which can trigger an out-of-bound read. The out-of-bounds read can be triggered via the main `gss_accept_sec_context` entry point and could cause a denial-of-service if the memory is unmapped. The issue is fixed in version 1.2.0.

## References
- https://github.com/gssapi/gss-ntlmssp/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25567.json
- https://github.com/gssapi/gss-ntlmssp/security/advisories/GHSA-24pf-6prf-24ch
- https://nvd.nist.gov/vuln/detail/CVE-2023-25567
- https://github.com/gssapi/gss-ntlmssp/commit/025fbb756d44ffee8f847db4222ed6aa4bd1fbe4
