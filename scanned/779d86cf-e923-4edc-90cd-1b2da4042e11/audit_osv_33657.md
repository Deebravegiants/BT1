# [C] Icinga 2 certificate renewal might incorrectly renew an invalid certificate

## Summary
Severity: Critical
Advisory: CVE-2025-48057
Aliases: GHSA-7vcf-f5v9-3wr6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-48057
Type: osv

## Details
Icinga 2 is a monitoring system which checks the availability of network resources, notifies users of outages, and generates performance data for reporting. Prior to versions 2.12.12, 2.13.12, and 2.14.6, the VerifyCertificate() function can be tricked into incorrectly treating certificates as valid. This allows an attacker to send a malicious certificate request that is then treated as a renewal of an already existing certificate, resulting in the attacker obtaining a valid certificate that can be used to impersonate trusted nodes. This only occurs when Icinga 2 is built with OpenSSL older than version 1.1.0. This issue has been patched in versions 2.12.12, 2.13.12, and 2.14.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48057.json
- https://github.com/Icinga/icinga2/security/advisories/GHSA-7vcf-f5v9-3wr6
- https://nvd.nist.gov/vuln/detail/CVE-2025-48057
- https://github.com/Icinga/icinga2/commit/34c93a2542bbe4e9886d15bc17ec929ead1aa152
- https://github.com/Icinga/icinga2/commit/4023128be42b18a011dda71ddee9ca79955b89cb
- https://github.com/Icinga/icinga2/commit/60f75f4a3d5cbb234eb3694ba7e9076a1a5b8776
- https://github.com/Icinga/icinga2/commit/9ad5683aab9eb392c6737ff46c830a945c9e240f
- https://github.com/Icinga/icinga2/commit/9b2c05d0cc09210bdeade77cf9a73859250fc48d
