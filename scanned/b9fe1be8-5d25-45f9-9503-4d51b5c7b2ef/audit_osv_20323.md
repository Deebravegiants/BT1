# [M] CVE-2021-32791

## Summary
Severity: Medium
Advisory: CVE-2021-32791
Aliases: GHSA-px3c-6x7j-3r9r
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-26
Source: https://osv.dev/vulnerability/CVE-2021-32791
Type: osv

## Details
mod_auth_openidc is an authentication/authorization module for the Apache 2.x HTTP server that functions as an OpenID Connect Relying Party, authenticating users against an OpenID Connect Provider. In mod_auth_openidc before version 2.4.9, the AES GCM encryption in mod_auth_openidc uses a static IV and AAD. It is important to fix because this creates a static nonce and since aes-gcm is a stream cipher, this can lead to known cryptographic issues, since the same key is being reused. From 2.4.9 onwards this has been patched to use dynamic values through usage of cjose AES encryption routines.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00034.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FZVF6BSJLRQZ7PFFR4X5JSU6KUJYNOCU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QXAWKPT5LXZSUTFSJ6IWSZC7RMYYQXQD/
- https://github.com/zmartzone/mod_auth_openidc/releases/tag/v2.4.9
- https://github.com/zmartzone/mod_auth_openidc/commit/375407c16c61a70b56fdbe13b0d2c8f11398e92c
- https://github.com/zmartzone/mod_auth_openidc/security/advisories/GHSA-px3c-6x7j-3r9r
- https://www.oracle.com/security-alerts/cpuapr2022.html
