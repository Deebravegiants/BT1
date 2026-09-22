# [C] CVE-2026-8470

## Summary
Severity: Critical
Advisory: CVE-2026-8470
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-8470
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3, 1.0.0 through 1.10.3, 1.0.0 through 1.10.3, and 1.0.0 through 1.10.3 use Python's non-cryptographic random module for generating Fernet encryption keys from user secrets under 32 characters. The deterministic Mersenne Twister PRNG produces identical keys for identical seeds, allowing attackers to reproduce encryption keys and decrypt stored API keys and authentication tokens.

## References
- https://www.ibm.com/support/pages/node/7282648
