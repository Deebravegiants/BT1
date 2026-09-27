# [C] CVE-2021-45079

## Summary
Severity: Critical
Advisory: CVE-2021-45079
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-01-31
Source: https://osv.dev/vulnerability/CVE-2021-45079
Type: osv

## Details
In strongSwan before 5.9.5, a malicious responder can send an EAP-Success message too early without actually authenticating the client and (in the case of EAP methods with mutual authentication and EAP-only authentication for IKEv2) even without server authentication.

## References
- https://www.strongswan.org/blog/2022/01/24/strongswan-vulnerability-%28cve-2021-45079%29.html
