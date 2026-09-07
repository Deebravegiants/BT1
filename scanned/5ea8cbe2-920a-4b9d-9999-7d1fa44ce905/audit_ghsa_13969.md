# [C] openssl-src contains Read Buffer Overflow in X.509 Name Constraint

## Summary
Severity: Critical
Advisory: GHSA-w67w-mw4j-8qrv
CVE: CVE-2022-4203
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-w67w-mw4j-8qrv
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.12

## Details
A read buffer overrun can be triggered in X.509 certificate verification, specifically in name constraint checking. Note that this occurs
after certificate chain signature verification and requires either a CA to have signed the malicious certificate or for the application to
continue certificate verification despite failure to construct a path to a trusted issuer.

The read buffer overrun might result in a crash which could lead to a denial of service attack. In theory it could also result in the disclosure of private memory contents (such as private keys, or sensitive plaintext) although we are not aware of any working exploit leading to memory contents disclosure as of the time of release of this advisory.

In a TLS client, this can be triggered by connecting to a malicious server. In a TLS server, this can be triggered if the server requests client authentication and a malicious client connects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4203
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=c927a3492698c254637da836762f9b1f86cffabc
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2023-0003
- https://rustsec.org/advisories/RUSTSEC-2023-0008.html
- https://security.gentoo.org/glsa/202402-08
- https://www.openssl.org/news/secadv/20230207.txt
