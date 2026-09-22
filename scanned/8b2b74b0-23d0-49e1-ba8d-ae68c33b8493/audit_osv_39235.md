# [H] CVE-2026-44690

## Summary
Severity: High
Advisory: CVE-2026-44690
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-44690
Type: osv

## Details
In NLnet Labs Unbound 1.7.0 up to and including 1.25.1, insufficient validation of the RRSIG.Labels field combined with premature cache writes during RFC 8198 aggressive NSEC processing leads to cache poisoning that permits a malicious actor controlling a single delegated zone to poison arbitrary sibling zones under NSEC-signed parent domains. A malicious actor with one registered domain under an NSEC-signed TLD can serve malicious insecure DNS responses for unrelated sibling domains (sharing the same parent zone). Arbitrary delegations that do not exist under the parent domain and are covered by the parent's NSEC chain can be brought into insecure existence by fraudulent wildcard DS records (less labels than expected, unknown algorithm) from the malicious sibling domain. This allows the malicious actor to inject insecure wildcard records for those delegations.

## References
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-44690.txt
