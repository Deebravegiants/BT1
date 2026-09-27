# [H] PAM-PKCS#11 vulnerable to authentication bypass with default value for `cert_policy` (`none`)

## Summary
Severity: High
Advisory: CVE-2025-24032
Aliases: GHSA-8r8p-7mgp-vf56
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:L/SI:L/SA:L)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/CVE-2025-24032
Type: osv

## Details
PAM-PKCS#11 is a Linux-PAM login module that allows a X.509 certificate based user login. Prior to version 0.6.13, if cert_policy is set to none (the default value), then pam_pkcs11 will only check if the user is capable of logging into the token. An attacker may create a different token with the user's public data (e.g. the user's certificate) and a PIN known to the attacker. If no signature with the private key is required, then the attacker may now login as user with that created token. The default to *not* check the private key's signature has been changed with commit commi6638576892b59a99389043c90a1e7dd4d783b921, so that all versions starting with pam_pkcs11-0.6.0 should be affected. As a workaround, in `pam_pkcs11.conf`, set at least `cert_policy = signature;`.

## References
- https://github.com/OpenSC/pam_pkcs11/releases/tag/pam_pkcs11-0.6.13
- https://lists.debian.org/debian-lts-announce/2025/02/msg00021.html
- https://www.vicarius.io/vsociety/posts/cve-2025-24032-detect-vulnerability-in-linux-pam-module
- https://www.vicarius.io/vsociety/posts/cve-2025-24032-mitigate-linux-pam-module-vulnerability
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24032.json
- https://github.com/OpenSC/pam_pkcs11/security/advisories/GHSA-8r8p-7mgp-vf56
- https://nvd.nist.gov/vuln/detail/CVE-2025-24032
- https://github.com/OpenSC/pam_pkcs11/commit/470263258d1ac59c5eade439c4d9caba0097e6e6
- https://github.com/OpenSC/pam_pkcs11/commit/b665b287ff955bbbd9539252ff9f9e2754c3fb48
- https://github.com/OpenSC/pam_pkcs11/commit/d9530167966a77115db6e885d459382a2e52ee9e
