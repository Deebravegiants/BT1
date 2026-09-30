# [H] X.509 Email Address Variable Length Buffer Overflow

## Summary
Severity: High
Advisory: GHSA-h8jm-2x53-xhp5
CVE: CVE-2022-3786
CWE: CWE-120
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-h8jm-2x53-xhp5
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.11

## Details
A buffer overrun can be triggered in X.509 certificate verification,
specifically in name constraint checking. Note that this occurs after
certificate chain signature verification and requires either a CA to
have signed a malicious certificate or for an application to continue
certificate verification despite failure to construct a path to a trusted
issuer. An attacker can craft a malicious email address in a certificate
to overflow an arbitrary number of bytes containing the `.` character
(decimal 46) on the stack. This buffer overflow could result in a crash
(causing a denial of service).

In a TLS client, this can be triggered by connecting to a malicious
server. In a TLS server, this can be triggered if the server requests
client authentication and a malicious client connects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3786
- https://github.com/rustsec/advisory-db/pull/1452
- https://github.com/alexcrichton/openssl-src-rs/commit/4a31c14f31e1a08c18893a37e304dd1dd4b7daa3
- https://github.com/openssl/openssl/commit/fe3b639dc19b325846f4f6801f2f4604f56e3de3
- https://www.openssl.org/news/secadv/20221101.txt
- https://www.kb.cert.org/vuls/id/794340
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-openssl-W9sdCc2a
- https://security.netapp.com/advisory/ntap-20221102-0001
- https://security.gentoo.org/glsa/202211-01
- https://rustsec.org/advisories/RUSTSEC-2022-0065.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0023
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DWP23EZYOBDJQP7HP4YU7W2ABU2YDITS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/63YRPWPUSX3MBHNPIEJZDKQT6YA7UF6S
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DWP23EZYOBDJQP7HP4YU7W2ABU2YDITS
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/63YRPWPUSX3MBHNPIEJZDKQT6YA7UF6S
- https://github.com/alexcrichton/openssl-src-rs
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=c42165b5706e42f67ef8ef4c351a9a4c5d21639a
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=c42165b5706e42f67ef8ef4c351a9a4c5d21639a
- http://packetstormsecurity.com/files/169687/OpenSSL-Security-Advisory-20221101.html
- http://www.openwall.com/lists/oss-security/2022/11/01/15
