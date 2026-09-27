# [C] FastGPT: Unauthenticated WeChat channel hijack and denial of service via shareId-only authorization

## Summary
Severity: Critical
Advisory: CVE-2026-68929
Aliases: GHSA-q4pr-3qpg-9q5v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-68929
Type: osv

## Details
FastGPT is an open-source LLM platform for building AI applications on a knowledge base. In versions prior to 4.15.2, the WeChat (iLink) share-channel endpoints authorize requests using only the public shareId, with no authenticated identity or team-ownership check. As a result, an unauthenticated attacker who knows a victim team's shareId can take that team's WeChat bot offline or hijack the channel to their own bot: the logout endpoint is gated only by an existence check yet wipes the outLink's stored WeChat token, and the QR-code status endpoint performs no authorization at all and writes attacker-supplied bot credentials into the outLink identified by shareId. By generating a QR for a victim shareId, scanning it with their own WeChat, and calling the status endpoint, an attacker binds the victim team's app to the attacker's bot, exposing the app's private responses, displacing the legitimate binding, and consuming the victim's resources. The shareId is exposed in every shared chat URL, iframe, and embed, so it is not a secret. This issue is fixed in version 4.15.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68929.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-q4pr-3qpg-9q5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-68929
- https://github.com/labring/FastGPT/commit/81d391995b1f9989455267448872ff88bb1f42c9
