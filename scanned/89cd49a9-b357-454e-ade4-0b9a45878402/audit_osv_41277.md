# [H] Apereo CAS 7.3.0 < 8.0.0-RC6 - AES-GCM Nonce Reuse Information Disclosure

## Summary
Severity: High
Advisory: CVE-2026-59099
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-59099
Type: osv

## Details
Apereo CAS 7.3.0 before 8.0.0-RC6 contains a cryptographic vulnerability that allows remote unauthenticated attackers to recover plaintext conversation state by exploiting AES-GCM initialization vector reuse across the server lifetime. Attackers can collect multiple client-side webflow execution tokens from the unauthenticated login page and perform known-plaintext analysis to decrypt the webflow conversation state due to keystream reuse caused by a fixed all-zero IV paired with the same encryption key.

## References
- https://apereo.github.io/2026/06/18/vuln/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59099.json
- https://github.com/apereo/cas/releases/tag/v8.0.0-RC6
- https://nvd.nist.gov/vuln/detail/CVE-2026-59099
- https://www.vulncheck.com/advisories/apereo-cas-rc6-aes-gcm-nonce-reuse-information-disclosure
- https://github.com/apereo/cas/commit/22c6f4adf738852782309b523b4e80371057f2d0
- https://github.com/apereo/cas
- https://github.com/geo-chen/oss/blob/main/cas.md
