# [H] Emissary May Use a Broken or Risky Cryptographic Algorithm

## Summary
Severity: High
Advisory: GHSA-hw43-fcmm-3m5g
CVE: CVE-2025-27508
CWE: CWE-327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-hw43-fcmm-3m5g
Type: github-advisory

## Affected
- Maven: `gov.nsa.emissary:emissary` — affected >=0 <8.24.0

## Details
### Summary
The ChecksumCalculator class within  allows for hashing and checksum generation, but it includes or defaults to algorithms that are no longer recommended for secure cryptographic use cases (e.g., SHA-1, CRC32, and SSDEEP). These algorithms, while possibly valid for certain non-security-critical tasks, can expose users to security risks if used in scenarios where strong cryptographic guarantees are required.

### Requirement from NIST
Requirement from NIST regarding SHA1

https://csrc.nist.gov/projects/hash-functions#:~:text=NIST%20deprecated%20the%20use%20of,use%20of%20the%20SHA%2D1.

> Federal agencies should use SHA-2 or SHA-3 as an alternative to SHA-1.
> Further guidance will be available soon. Send questions on the transition to sha-1-transition@nist.gov.

https://www.nist.gov/news-events/news/2022/12/nist-retires-sha-1-cryptographic-algorithm

### Mitigation and Fix
Make it clear to developers and users that the ChecksumCalculator is specific to the "Known File Filter" (KFF) document similarity feature and is not intended to suggest or endorse global use as a cryptographically secure hashing or checksum mechanism.

While these specific default insecure algorithms can not be updated without violating the intended use-case, it can be clearly documented and prevented using better access modifiers in the ChecksumCalculator class.

### Details
Within ChecksumCalculator.java, the following points raise potential security concerns:

SHA-1:
SHA-1 has been widely deprecated for cryptographic purposes due to known collision attacks.
The constructor defaults to "SHA-1" if no specific algorithm is provided.
CRC32:
CRC32 is a simple checksum mechanism, not a cryptographic hash function. It is unsuitable for security-critical integrity checks since it can be easily manipulated or collided.
SSDEEP (Fuzzy Hashing):
SSDEEP is a context-specific tool used for similarity matching and may not be a secure cryptographic function for authentication or tamper detection.
There is no apparent mechanism to prevent developers from using these weaker algorithms in security-sensitive contexts. Users of emissary who rely on ChecksumCalculator for strong security guarantees (e.g., data integrity or authentication) may be misled into assuming these algorithms provide adequate protection.

### PoC
Code could be found https://github.com/NationalSecurityAgency/emissary/blob/main/src/main/java/emissary/kff/ChecksumCalculator.java

### Impact
Impact
Weakened Security Posture: Applications integrating Emissary may inadvertently use these algorithms in a way that could be exploited (e.g., collisions in SHA-1, trivial collisions in CRC32).
Misleading Assurance: Developers might assume Emissary’s recommended defaults are secure for cryptographic validation, which can result in insecure implementations.
Potential for Collision Attacks: Attackers could craft inputs that yield the same SHA-1 hash or manipulate CRC32 sums, thus bypassing naive integrity checks.
Because this project is produced under the NSA umbrella, users may have an inflated trust in its security posture, potentially leading them to rely on these algorithms in high-security environments without recognizing the associated risks.

## References
- https://github.com/NationalSecurityAgency/emissary/security/advisories/GHSA-hw43-fcmm-3m5g
- https://nvd.nist.gov/vuln/detail/CVE-2025-27508
- https://github.com/NationalSecurityAgency/emissary/commit/da3a81a8977577597ff2a944820a5ae4e9762368
- https://github.com/NationalSecurityAgency/emissary
- https://github.com/NationalSecurityAgency/emissary/releases/tag/8.24.0
