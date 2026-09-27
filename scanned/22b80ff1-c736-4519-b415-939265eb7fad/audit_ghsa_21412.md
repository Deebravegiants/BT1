# [C] X.509 Email Address 4-byte Buffer Overflow

## Summary
Severity: Critical
Advisory: GHSA-8rwr-x37p-mx23
CVE: CVE-2022-3602
CWE: CWE-120, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-01
Source: https://github.com/advisories/GHSA-8rwr-x37p-mx23
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.11

## Details
A buffer overrun can be triggered in X.509 certificate verification, specifically in name constraint checking. Note that this occurs
after certificate chain signature verification and requires either a CA to have signed the malicious certificate or for the application to
continue certificate verification despite failure to construct a path to a trusted issuer. An attacker can craft a malicious email address
to overflow four attacker-controlled bytes on the stack. This buffer overflow could result in a crash (causing a denial of service) or
potentially remote code execution.

Many platforms implement stack overflow protections which would mitigate against the risk of remote code execution. The risk may be further mitigated based on stack layout for any given platform/compiler.

Pre-announcements of CVE-2022-3602 described this issue as CRITICAL. Further analysis based on some of the mitigating factors described above have led this to be downgraded to HIGH. Users are still encouraged to upgrade to a new version as soon as possible.

In a TLS client, this can be triggered by connecting to a malicious server. In a TLS server, this can be triggered if the server requests client authentication and a malicious client connects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3602
- https://github.com/rustsec/advisory-db/pull/1452
- https://github.com/alexcrichton/openssl-src-rs/commit/4a31c14f31e1a08c18893a37e304dd1dd4b7daa3
- https://github.com/openssl/openssl/commit/fe3b639dc19b325846f4f6801f2f4604f56e3de3
- https://www.openssl.org/news/secadv/20221101.txt
- https://www.kb.cert.org/vuls/id/794340
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00789.html
- https://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-openssl-W9sdCc2a
- https://security.netapp.com/advisory/ntap-20221102-0001
- https://security.gentoo.org/glsa/202211-01
- https://rustsec.org/advisories/RUSTSEC-2022-0064.html
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0023
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DWP23EZYOBDJQP7HP4YU7W2ABU2YDITS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/63YRPWPUSX3MBHNPIEJZDKQT6YA7UF6S
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DWP23EZYOBDJQP7HP4YU7W2ABU2YDITS
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/63YRPWPUSX3MBHNPIEJZDKQT6YA7UF6S
- https://github.com/alexcrichton/openssl-src-rs
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=fe3b639dc19b325846f4f6801f2f4604f56e3de3
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=fe3b639dc19b325846f4f6801f2f4604f56e3de3
- http://packetstormsecurity.com/files/169687/OpenSSL-Security-Advisory-20221101.html
