# [H] OpenAM: Unauthenticated Authentication Bypass via RADIUS Spoofing

## Summary
Severity: High
Advisory: GHSA-386j-6m86-78f9
CVE: CVE-2026-46560
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-386j-6m86-78f9
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-radius` — affected >=0 <16.1.1

## Details
## Summary

**Description**

An Improper Verification of Cryptographic Signature (CWE-347) issue in OpenAM's RADIUS authentication module allows an unauthenticated network attacker to spoof an Access-Accept response and obtain an OpenAM session for any RADIUS username, without knowing the configured shared secret. This affects OpenAM Community Edition through version 16.0.6 and was patched in version 16.1.1.

The RADIUS client opens an unconnected datagram socket and treats the first UDP datagram delivered to its source port as authoritative. The receive path does not check the source IP/port, does not match the response identifier to the outstanding request, and does not verify the Response Authenticator (RFC 2865 §3); the RFC 2869 Message-Authenticator is neither sent nor required. Any non-Reject/non-Challenge packet is treated as success, so a forged Access-Accept is accepted as a valid login.

## Impact
OpenAM Community Edition deployments through version 16.0.6 where an administrator has enabled a RADIUS module instance on a login chain are potentially affected. An attacker either races the real server on-path, or off-path sprays forged Access-Accept packets at the OpenAM client port. Because the client performs no verification of the response authenticator, no MD5 chosen-prefix forgery is required, which is is materially stronger than the BlastRADIUS family (CVE-2024-3596), in which an attacker must still forge a valid authenticator.

Successful exploitation yields pre-authentication impersonation of any RADIUS-mapped user in any affected realm. The resulting session is indistinguishable from a legitimate RADIUS login and carries the named principal's privileges.

## Patch
This has been patched in OpenAM Community Edition version 16.1.1. Users are encouraged to update to the latest release.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-386j-6m86-78f9
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.1
