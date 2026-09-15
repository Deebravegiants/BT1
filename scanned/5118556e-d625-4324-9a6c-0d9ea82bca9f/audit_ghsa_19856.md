# [M] Post-Quantum Secure Feldman's Verifiable Secret Sharing has Timing Side-Channels in Matrix Operations

## Summary
Severity: Medium
Advisory: GHSA-q65w-fg65-79f4
CVE: CVE-2025-29780
CWE: CWE-203, CWE-208, CWE-385
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-q65w-fg65-79f4
Type: github-advisory

## Affected
- PyPI: `PostQuantum-Feldman-VSS` — affected >=0

## Details
**Description:**

The `feldman_vss` library contains timing side-channel vulnerabilities in its matrix operations, specifically within the `_find_secure_pivot` function and potentially other parts of `_secure_matrix_solve`. These vulnerabilities are due to Python's execution model, which does not guarantee constant-time execution. An attacker with the ability to measure the execution time of these functions (e.g., through repeated calls with carefully crafted inputs) could potentially recover secret information used in the Verifiable Secret Sharing (VSS) scheme.

The `_find_secure_pivot` function, used during Gaussian elimination in `_secure_matrix_solve`, attempts to find a non-zero pivot element. However, the conditional statement `if matrix[row][col] != 0 and row_random < min_value:` has execution time that depends on the value of `matrix[row][col]`. This timing difference can be exploited by an attacker.

The `constant_time_compare` function in this file also does not provide a constant-time guarantee.

This advisory formalizes the timing side-channel vulnerabilities already documented in the library's "Known Security Vulnerabilities" section. The Python implementation of matrix operations in the _find_secure_pivot and _secure_matrix_solve functions cannot guarantee constant-time execution, potentially leaking information about secret polynomial coefficients.

An attacker with the ability to make precise timing measurements of these operations could potentially extract secret information through statistical analysis of execution times, though practical exploitation would require significant expertise and controlled execution environments.

**Impact:**

Successful exploitation of these timing side-channels could allow an attacker to recover secret keys or other sensitive information protected by the VSS scheme.  This could lead to a complete compromise of the shared secret.

**References:**

*   File: `feldman_vss.py`
*   Function: `_find_secure_pivot`
*   Function: `_secure_matrix_solve`
*   Function: `constant_time_compare`
*   [Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems (1996)](https://www.rambus.com/wp-content/uploads/2015/08/TimingAttacks.pdf) - A seminal paper on timing attacks.
*   [Side-Channel Attacks](https://en.wikipedia.org/wiki/Side-channel_attack) - Wikipedia article on side-channel attacks.

**Remediation:**

As acknowledged in the library's documentation, these vulnerabilities cannot be adequately addressed in pure Python. The advisory recommends:

1. SHORT TERM: Consider using this library only in environments where timing measurements by attackers are infeasible.

2. MEDIUM TERM: Implement your own wrappers around critical operations using constant-time libraries in languages like Rust, Go, or C.

3. LONG TERM: Wait for the planned Rust implementation mentioned in the library documentation that will properly address these issues.

Note that the usage of random.Random() identified in the _refresh_shares_additive function is intentional and secure as documented in the "False-Positive Vulnerabilities" section of the code, and should not be considered part of this vulnerability.

## References
- https://github.com/DavidOsipov/PostQuantum-Feldman-VSS/security/advisories/GHSA-q65w-fg65-79f4
- https://nvd.nist.gov/vuln/detail/CVE-2025-29780
- https://en.wikipedia.org/wiki/Side-channel_attack
- https://github.com/DavidOsipov/PostQuantum-Feldman-VSS
- https://www.rambus.com/wp-content/uploads/2015/08/TimingAttacks.pdf
