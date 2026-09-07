# [C] MsQuic has a Remote Elevation of Privilege Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-gvvw-8j96-8g5r
CVE: CVE-2026-32179
CWE: CWE-191
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-gvvw-8j96-8g5r
Type: github-advisory

## Affected
- NuGet: `Microsoft.Native.Quic.MsQuic.OpenSSL` — affected >=2.5.0-ci.532574 <2.5.7
- NuGet: `Microsoft.Native.Quic.MsQuic.Schannel` — affected >=2.5.0-ci.532574 <2.5.7
- NuGet: `Microsoft.Native.Quic.MsQuic.Schannel` — affected >=0 <2.4.18
- NuGet: `Microsoft.Native.Quic.MsQuic.OpenSSL` — affected >=0 <2.4.18

## Details
### Summary
Improper input validation in Microsoft QUIC allows an unauthorized attacker to elevate privileges over a network.

### Details
 Improper Input Validation Integer Underflow (Wrap or Wraparound) when decoding ACK frame.

#### Patches
- Fix underflow in ACK frame parsing - 1e6e999b

### Impact
An attacker who successfully exploited this vulnerability could gain elevated privileges.

## References
- https://github.com/microsoft/msquic/security/advisories/GHSA-gvvw-8j96-8g5r
- https://github.com/microsoft/msquic/commit/1e6e999b199430effeefee3d85baa0c9dd35ad5e
- https://github.com/microsoft/msquic
