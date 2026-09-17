# [M] ALPINE-CVE-2020-1971

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-1971
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-1971
Type: osv

## Affected
- Alpine:v3.13: `libressl` — affected >=0 <3.1.5-r0
- Alpine:v3.10: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.11: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.12: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.13: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.14: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.15: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.16: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.17: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.18: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.19: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.20: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.21: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.22: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.23: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.24: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.9: `openssl` — affected >=1.0.2 <1.1.1i-r0
- Alpine:v3.15: `openssl3` — affected >=0 <1.1.1i-r0
- Alpine:v3.16: `openssl3` — affected >=0 <1.1.1i-r0

## Details
The X.509 GeneralName type is a generic type for representing different types of names. One of those name types is known as EDIPartyName. OpenSSL provides a function GENERAL_NAME_cmp which compares different instances of a GENERAL_NAME to see if they are equal or not. This function behaves incorrectly when both GENERAL_NAMEs contain an EDIPARTYNAME. A NULL pointer dereference and a crash may occur leading to a possible denial of service attack. OpenSSL itself uses the GENERAL_NAME_cmp function for two purposes: 1) Comparing CRL distribution point names between an available CRL and a CRL distribution point embedded in an X509 certificate 2) When verifying that a timestamp response token signer matches the timestamp authority name (exposed via the API functions TS_RESP_verify_response and TS_RESP_verify_token) If an attacker can control both items being compared then that attacker could trigger a crash. For example if the attacker can trick a client or server into checking a malicious certificate against a malicious CRL then this may occur. Note that some applications automatically download CRLs based on a URL embedded in a certificate. This checking happens prior to the signatures on the certificate and CRL being verified. OpenSSL's s_server, s_client and verify tools have support for the "-crl_download" option which implements automatic CRL downloading and this attack has been demonstrated to work against those tools. Note that an unrelated bug means that affected versions of OpenSSL cannot parse or construct correct encodings of EDIPARTYNAME. However it is possible to construct a malformed EDIPARTYNAME that OpenSSL's parser will accept and hence trigger this attack. All OpenSSL 1.1.1 and 1.0.2 versions are affected by this issue. Other OpenSSL releases are out of support and have not been checked. Fixed in OpenSSL 1.1.1i (Affected 1.1.1-1.1.1h). Fixed in OpenSSL 1.0.2x (Affected 1.0.2-1.0.2w).

## References
- https://security.alpinelinux.org/vuln/CVE-2020-1971
