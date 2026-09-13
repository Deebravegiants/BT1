# [M] Sakai kernel-impl: predictable PRNG used to generate server‑side encryption key in EncryptionUtilityServiceImpl

## Summary
Severity: Medium
Advisory: GHSA-gr7h-xw4f-wh86
CVE: CVE-2025-62710
CWE: CWE-337
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-gr7h-xw4f-wh86
Type: github-advisory

## Affected
- Maven: `org.sakaiproject.kernel:sakai-kernel-impl` — affected >=0

## Details
### Impact
EncryptionUtilityServiceImpl initialized an AES256TextEncryptor password (serverSecretKey) using RandomStringUtils with the default java.util.Random. java.util.Random is a non‑cryptographic PRNG and can be predicted from limited state/seed information (e.g., start time window), substantially reducing the effective search space of the generated key. An attacker who can obtain ciphertexts (e.g., exported or at‑rest strings protected by this service) and approximate the PRNG seed can feasibly reconstruct the serverSecretKey and decrypt affected data.

### Patches
SAK-49866 is patched in Sakai 23.5, 25.0, and trunk. 

### Credits
- Reported by [Suraj Gangwar](https://www.linkedin.com/in/surajgangwar?trk=contact-info).
- Patched by Sam Ottenhoff (Longsight).

## References
- https://github.com/sakaiproject/sakai/security/advisories/GHSA-gr7h-xw4f-wh86
- https://nvd.nist.gov/vuln/detail/CVE-2025-62710
- https://github.com/sakaiproject/sakai/commit/bde070104b1de01f4a6458dca6d9e0880a0e3c04
- https://github.com/sakaiproject/sakai
