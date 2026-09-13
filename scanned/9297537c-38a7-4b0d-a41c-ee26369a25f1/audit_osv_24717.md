# [H] GSS-NTLMSSP vulnerable to incorrect free when decoding target information

## Summary
Severity: High
Advisory: CVE-2023-25565
Aliases: GHSA-7q7f-wqcg-mvfg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-14
Source: https://osv.dev/vulnerability/CVE-2023-25565
Type: osv

## Details
GSS-NTLMSSP is a mechglue plugin for the GSSAPI library that implements NTLM authentication. Prior to version 1.2.0, an incorrect free when decoding target information can trigger a denial of service. The error condition incorrectly assumes the `cb` and `sh` buffers contain a copy of the data that needs to be freed. However, that is not the case. This vulnerability can be triggered via the main `gss_accept_sec_context` entry point. This will likely trigger an assertion failure in `free`, causing a denial-of-service. This issue is fixed in version 1.2.0.

## References
- https://github.com/gssapi/gss-ntlmssp/releases/tag/v1.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25565.json
- https://github.com/gssapi/gss-ntlmssp/security/advisories/GHSA-7q7f-wqcg-mvfg
- https://nvd.nist.gov/vuln/detail/CVE-2023-25565
- https://github.com/gssapi/gss-ntlmssp/commit/c16100f60907a2de92bcb676f303b81facee0f64
