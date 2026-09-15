# [H] Certifi removes GLOBALTRUST root certificate

## Summary
Severity: High
Advisory: CVE-2024-39689
Aliases: GHSA-248v-346w-9cwc, PYSEC-2024-230
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39689
Type: osv

## Details
Certifi is a curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. Certifi starting in 2021.5.30 and prior to 2024.7.4 recognized root certificates from `GLOBALTRUST`. Certifi 2024.7.04 removes root certificates from `GLOBALTRUST` from the root store. These are in the process of being removed from Mozilla's trust store. `GLOBALTRUST`'s root certificates are being removed pursuant to an investigation which identified "long-running and unresolved compliance issues."

## References
- https://groups.google.com/a/mozilla.org/g/dev-security-policy/c/XpknYMPO8dI
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39689.json
- https://github.com/certifi/python-certifi/security/advisories/GHSA-248v-346w-9cwc
- https://nvd.nist.gov/vuln/detail/CVE-2024-39689
- https://security.netapp.com/advisory/ntap-20241206-0001/
- https://github.com/certifi/python-certifi/commit/bd8153872e9c6fc98f4023df9c2deaffea2fa463
