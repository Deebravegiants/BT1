# [C] CVE-2021-32639

## Summary
Severity: Critical
Advisory: CVE-2021-32639
Aliases: GHSA-2p8j-2rf3-h4xr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-07-02
Source: https://osv.dev/vulnerability/CVE-2021-32639
Type: osv

## Details
Emissary is a P2P-based, data-driven workflow engine. Emissary version 6.4.0 is vulnerable to Server-Side Request Forgery (SSRF). In particular, the `RegisterPeerAction` endpoint and the `AddChildDirectoryAction` endpoint are vulnerable to SSRF. This vulnerability may lead to credential leaks. Emissary version 7.0 contains a patch. As a workaround, disable network access to Emissary from untrusted sources.

## References
- https://github.com/NationalSecurityAgency/emissary/blob/30c54ef16c6eb6ed09604a929939fb9f66868382/src/main/java/emissary/server/mvc/internal/AddChildDirectoryAction.java
- https://github.com/NationalSecurityAgency/emissary/blob/30c54ef16c6eb6ed09604a929939fb9f66868382/src/main/java/emissary/server/mvc/internal/RegisterPeerAction.java
- https://github.com/NationalSecurityAgency/emissary/security/advisories/GHSA-2p8j-2rf3-h4xr
