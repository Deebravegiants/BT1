# [M] Post-Quantum Secure Feldman's Verifiable Secret Sharing has Inadequate Fault Injection Countermeasures in `secure_redundant_execution`

## Summary
Severity: Medium
Advisory: GHSA-r8gc-qc2c-c7vh
CVE: CVE-2025-29779
CWE: CWE-1240
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:P/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-r8gc-qc2c-c7vh
Type: github-advisory

## Affected
- PyPI: `PostQuantum-Feldman-VSS` — affected >=0

## Details
**Description:**

The `secure_redundant_execution` function in feldman_vss.py attempts to mitigate fault injection attacks by executing a function multiple times and comparing results. However, several critical weaknesses exist:

1. Python's execution environment cannot guarantee true isolation between redundant executions
2. The constant-time comparison implementation in Python is subject to timing variations
3. The randomized execution order and timing provide insufficient protection against sophisticated fault attacks
4. The error handling may leak timing information about partial execution results

These limitations make the protection ineffective against targeted fault injection attacks, especially from attackers with physical access to the hardware.

**Impact:**

A successful fault injection attack could allow an attacker to:

1. Bypass the redundancy check mechanisms
2. Extract secret polynomial coefficients during share generation or verification
3. Force the acceptance of invalid shares during verification
4. Manipulate the commitment verification process to accept fraudulent commitments

This undermines the core security guarantees of the Verifiable Secret Sharing scheme.

**References:**

*   File: `feldman_vss.py`
*   Function: `secure_redundant_execution`
*   [Fault Attacks](https://en.wikipedia.org/wiki/Fault_attack) - Wikipedia article on fault attacks.
*   Bar-El, H., et al. "The Sorcerer's Apprentice Guide to Fault Attacks" - https://eprint.iacr.org/2004/100.pdf
* CWE-1279: https://cwe.mitre.org/data/definitions/1279.html
* NIST SP 800-90B section on implementation validation


**Remediation:**

Long-term remediation requires reimplementing the security-critical functions in a lower-level language like Rust.

Short-term mitigations:

1. Deploy the software in environments with physical security controls
2. Increase the redundancy count (from 5 to a higher number) by modifying the source code
3. Add external verification of cryptographic operations when possible
4. Consider using hardware security modules (HSMs) for key operations

## References
- https://github.com/DavidOsipov/PostQuantum-Feldman-VSS/security/advisories/GHSA-r8gc-qc2c-c7vh
- https://nvd.nist.gov/vuln/detail/CVE-2025-29779
- https://en.wikipedia.org/wiki/Fault_attack
- https://eprint.iacr.org/2004/100.pdf
- https://github.com/DavidOsipov/PostQuantum-Feldman-VSS
