# [H] Denial of service when manipulating mod_auth_openidc_session_chunks cookie in mod_auth_openidc

## Summary
Severity: High
Advisory: CVE-2024-24814
Aliases: GHSA-hxr6-w4gc-7vvv
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-13
Source: https://osv.dev/vulnerability/CVE-2024-24814
Type: osv

## Details
mod_auth_openidc is an OpenID Certified™ authentication and authorization module for the Apache 2.x HTTP server that implements the OpenID Connect Relying Party functionality. In affected versions missing input validation on mod_auth_openidc_session_chunks cookie value makes the server vulnerable to a denial of service (DoS) attack. An internal security audit has been conducted and the reviewers found that if they manipulated the value of the mod_auth_openidc_session_chunks cookie to a very large integer, like 99999999, the server struggles with the request for a long time and finally gets back with a 500 error. Making a few requests of this kind caused our server to become unresponsive. Attackers can craft requests that would make the server work very hard (and possibly become unresponsive) and/or crash with minimal effort. This issue has been addressed in version 2.4.15.2. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/03/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/T7DKVEVREYAI4F46CQAVOTPL75WLOZOE/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24814.json
- https://github.com/OpenIDC/mod_auth_openidc/security/advisories/GHSA-hxr6-w4gc-7vvv
- https://nvd.nist.gov/vuln/detail/CVE-2024-24814
- https://github.com/OpenIDC/mod_auth_openidc/commit/4022c12f314bd89d127d1be008b1a80a08e1203d
