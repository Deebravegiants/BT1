# [H] mod_auth_openidc core dump when OIDCStripCookies is set and an empty Cookie header is supplied

## Summary
Severity: High
Advisory: CVE-2023-28625
Aliases: GHSA-f5xw-rvfr-24qr
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-03
Source: https://osv.dev/vulnerability/CVE-2023-28625
Type: osv

## Details
mod_auth_openidc is an authentication and authorization module for the Apache 2.x HTTP server that implements the OpenID Connect Relying Party functionality. In versions 2.0.0 through 2.4.13.1, when `OIDCStripCookies` is set and a crafted cookie supplied, a NULL pointer dereference would occur, resulting in a segmentation fault. This could be used in a Denial-of-Service attack and thus presents an availability risk. Version 2.4.13.2 contains a patch for this issue. As a workaround, avoid using `OIDCStripCookies`.

## References
- https://github.com/OpenIDC/mod_auth_openidc/blame/3f11976dab56af0a46a7dddb7a275cc16d6eb726/src/mod_auth_openidc.c#L178-L179
- https://github.com/OpenIDC/mod_auth_openidc/releases/tag/v2.4.13.2
- https://lists.debian.org/debian-lts-announce/2023/04/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WIBKFC22PDH6UXMSZ23PHTD7736ZC7BB/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28625.json
- https://github.com/OpenIDC/mod_auth_openidc/security/advisories/GHSA-f5xw-rvfr-24qr
- https://nvd.nist.gov/vuln/detail/CVE-2023-28625
- https://www.debian.org/security/2023/dsa-5405
- https://github.com/OpenIDC/mod_auth_openidc/commit/c0e1edac3c4c19988ccdc7713d7aebfce6ff916a
