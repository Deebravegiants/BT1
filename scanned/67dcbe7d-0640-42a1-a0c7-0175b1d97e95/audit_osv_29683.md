# [M] Sunshine has incorrect state management during pairing process may lead to incorrectly authorized client

## Summary
Severity: Medium
Advisory: CVE-2024-45407
Aliases: GHSA-jqph-8cp5-g874
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/CVE-2024-45407
Type: osv

## Details
Sunshine is a self-hosted game stream host for Moonlight. Clients that experience a MITM attack during the pairing process may inadvertantly allow access to an unintended client rather than failing authentication due to a PIN validation error. The pairing attempt fails due to the incorrect PIN, but the certificate from the forged pairing attempt is incorrectly persisted prior to the completion of the pairing request. This allows access to the certificate belonging to the attacker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45407.json
- https://github.com/LizardByte/Sunshine/security/advisories/GHSA-jqph-8cp5-g874
- https://nvd.nist.gov/vuln/detail/CVE-2024-45407
- https://github.com/LizardByte/Sunshine/commit/5fcd07ecb1428bfe245ad6fa349aead476c7e772
- https://github.com/LizardByte/Sunshine/commit/fd7e68457a134102d1b30af5796c79f2aa623224
