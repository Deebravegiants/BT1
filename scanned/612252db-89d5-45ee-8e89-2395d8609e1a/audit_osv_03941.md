# [M] ALPINE-CVE-2026-71225

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-71225
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-71225
Type: osv

## Affected
- Alpine:v3.21: `libkcapi` — affected >=0.10.1 <1.5.1-r0
- Alpine:v3.22: `libkcapi` — affected >=0.10.1 <1.5.1-r0
- Alpine:v3.23: `libkcapi` — affected >=0.10.1 <1.5.1-r0
- Alpine:v3.24: `libkcapi` — affected >=0.10.1 <1.5.1-r0

## Details
A flaw was found in libkcapi. When performing one-shot symmetric cipher operations on large inputs (over 64 KiB) in stateful modes such as Counter (CTR) or Cipher Block Chaining (CBC), the library improperly reuses the Initialization Vector (IV) for each internal data chunk. A remote attacker could potentially exploit this by making an application that uses libkcapi process specially crafted large inputs. This can lead to a significant weakening of data confidentiality, as the repeated IV use can expose relationships in encrypted plaintext, and may also affect data integrity by causing incorrect cryptographic processing.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-71225
