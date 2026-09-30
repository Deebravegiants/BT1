# [M] mod_gnutls missing key purpose check in client certificate verification

## Summary
Severity: Medium
Advisory: CVE-2026-33308
Aliases: GHSA-hm2g-m958-8qgh
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33308
Type: osv

## Details
Mod_gnutls is a TLS module for Apache HTTPD based on GnuTLS. Prior to version 0.13.0, code for client certificate verification did not check the key purpose as set in the Extended Key Usage extension. An attacker with access to the private key for a valid certificate issued by a CA trusted for TLS client authentication but designated for a different purpose could have used that certificate to improperly access resources requiring TLS client authentication. Server configurations that do not use client certificates (`GnuTLSClientVerify ignore`, the default) are not affected. The problem has been fixed in version 0.13.0 by rewriting certificate verification to use `gnutls_certificate_verify_peers()`, and requiring key purpose id-kp-clientAuth (also known as `tls_www_client` in GnuTLS) by default if the Extended Key Usage extension is present. The new `GnuTLSClientKeyPurpose` option allows overriding the expected key purpose if needed (please see the manual for details). Behavior for certificates without an Extended Key Usage extension is unchanged. If dedicated (sub-)CAs are used for issuing TLS client certificates only (not for any other purposes) the issue has no practical impact.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33308.json
- https://github.com/airtower-luna/mod_gnutls/security/advisories/GHSA-hm2g-m958-8qgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33308
