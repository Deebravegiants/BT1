# [C] Botan has a certificate authentication bypass due to trust anchor confusion

## Summary
Severity: Critical
Advisory: CVE-2026-34580
Aliases: GHSA-v782-6fq4-q827
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-34580
Type: osv

## Details
Botan is a C++ cryptography library. In 3.11.0, the function Certificate_Store::certificate_known had a misleading name; it would return true if any certificate in the store had a DN (and subject key identifier, if set) matching that of the argument. It did not check that the cert it found and the cert it was passed were actually the same certificate. In 3.11.0 an extension of path validation logic was made which assumed that certificate_known only returned true if the certificates were in fact identical. The impact is that if an end entity certificate is presented, and its DN (and subject key identifier, if set) match that of any trusted root, the end entity certificate is accepted immediately as if it itself were a trusted root. , This vulnerability is fixed in 3.11.1.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34580.json
- https://access.redhat.com/security/cve/CVE-2026-34580
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34580.json
- https://github.com/randombit/botan/security/advisories/GHSA-v782-6fq4-q827
- https://nvd.nist.gov/vuln/detail/CVE-2026-34580
- https://bugzilla.redhat.com/show_bug.cgi?id=2456288
