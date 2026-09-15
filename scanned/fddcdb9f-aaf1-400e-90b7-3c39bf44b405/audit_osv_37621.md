# [C] Lockfile checksums not verified in Hex allows dependency integrity bypass

## Summary
Severity: Critical
Advisory: CVE-2026-32148
Aliases: EEF-CVE-2026-32148, GHSA-hmv9-4mfr-m92v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-32148
Type: osv

## Details
Insufficient Verification of Data Authenticity vulnerability in hexpm hex (Hex.RemoteConverger module) allows dependency integrity bypass via unverified lockfile checksums.

Hex stores checksums for dependencies in the mix.lock file to ensure reproducible and integrity-checked builds. However, Hex.RemoteConverger.verify_resolved/2 never executes checksum verification because the lock data returned by Hex.Utils.lock/1 uses string-based dependency names, while the verification logic compares against atom-based names. This type mismatch causes the verification code path to be silently skipped. Checksums are still validated when packages are initially downloaded from the registry, but mismatches between the lockfile and resolved dependencies are not detected.

An attacker who can influence cached packages (e.g., via local cache poisoning or a compromised registry) can provide modified dependency contents that will be accepted without detection. The mix.lock file is silently rewritten with the checksum values from the registry, erasing evidence of tampering.

This issue affects hex: from 0.16.0 before 2.4.2.

## References
- https://cna.erlef.org/cves/CVE-2026-32148.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-32148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32148.json
- https://github.com/hexpm/hex/security/advisories/GHSA-hmv9-4mfr-m92v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32148
- https://github.com/hexpm/hex/commit/d7528c8199a1144511508bf3a6460026a5a14c8e
- https://github.com/hexpm/hex
- https://github.com/hexpm/hex.git
