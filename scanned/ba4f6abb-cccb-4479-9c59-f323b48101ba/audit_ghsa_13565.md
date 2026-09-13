# [H] Remote Denial of Service Vulnerability in Microsoft.Native.Quic.MsQuic.Schannel

## Summary
Severity: High
Advisory: GHSA-xh5m-8qqp-c5x7
CVE: CVE-2023-38171
CWE: CWE-400, CWE-476
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-xh5m-8qqp-c5x7
Type: github-advisory

## Affected
- NuGet: `Microsoft.Native.Quic.MsQuic.Schannel` — affected >=0 <2.2.3
- NuGet: `Microsoft.Native.Quic.MsQuic.OpenSSL` — affected >=0 <2.2.3

## Details
### Impact
The MsQuic server application or process will crash, resulting in a denial of service.

### Patches
The following patch was made:

- Don't Allow Version Negotiation Packets for Server Connections - https://github.com/microsoft/msquic/commit/3226cff07d22662f16fc98d605656860e64cd343

### Workarounds
Beyond upgrading to the patched versions, there is no other workaround. You must upgrade or disable MsQuic functionality.

## References
- https://github.com/microsoft/msquic/security/advisories/GHSA-xh5m-8qqp-c5x7
- https://nvd.nist.gov/vuln/detail/CVE-2023-38171
- https://github.com/microsoft/msquic/commit/3226cff07d22662f16fc98d605656860e64cd343
- https://github.com/microsoft/msquic
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-38171
