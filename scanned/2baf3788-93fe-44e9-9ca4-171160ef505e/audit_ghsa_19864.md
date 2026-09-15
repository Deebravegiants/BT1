# [H] PostQuantum-Feldman-VSS'S Dependency Vulnerability in gmpy2 Leading to Interpreter Crash

## Summary
Severity: High
Advisory: GHSA-v432-7f47-9g94
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-v432-7f47-9g94
Type: github-advisory

## Affected
- PyPI: `PostQuantum-Feldman-VSS` — affected >=0 <0.7.7b0

## Details
**Description:**

PostQuantum-Feldman-VSS, a Python library implementing Feldman's Verifiable Secret Sharing scheme with post-quantum security, was vulnerable to denial-of-service attacks in versions up to and including 0.7.6b0.  This vulnerability stems from the library's reliance on the `gmpy2` library for arbitrary-precision arithmetic.  `gmpy2`, in turn, depends on the GNU Multiple Precision Arithmetic Library (GMP). GMP, by design, terminates the process when it cannot allocate memory.  An attacker could exploit this by providing carefully crafted inputs that cause `gmpy2` to attempt to allocate extremely large amounts of memory, leading to a crash of the Python interpreter and thus a denial of service.

**Vulnerability Details:**

The core issue lies in the behavior of GMP (and thus, `gmpy2`) when memory allocation fails.  Instead of raising a standard Python exception that could be caught and handled, GMP terminates the entire process. This behavior is documented in the GMP and gmpy2 documentation:

*   **GMP Memory Management:** [https://gmplib.org/manual/Memory-Management](https://gmplib.org/manual/Memory-Management) (States that the default behavior is to terminate the program.)
*   **gmpy2 Overview:** [https://gmpy2.readthedocs.io/en/latest/overview.html](https://gmpy2.readthedocs.io/en/latest/overview.html) (Warns that `gmpy2` can crash the interpreter on memory allocation failure.)

Specific operations within the PostQuantum-Feldman-VSS library that were particularly vulnerable include:

*   **Large Exponentiation (`exp`, `secure_exp`):**  Exponentiation with very large bases or exponents can lead to extremely large results, consuming excessive memory.
*   **Multi-exponentiation (`efficient_multi_exp`):**  Similar to exponentiation, but with multiple bases and exponents, increasing the risk.
*   **Matrix Operations (`_secure_matrix_solve`):**  Large matrices used in polynomial reconstruction could lead to significant memory usage.
*   **Polynomial Evaluation (`_evaluate_polynomial`):** Evaluating polynomials with large coefficients or at large values of `x` could trigger excessive memory allocation.

**Mitigations in 0.8.0b2:**

Version 0.8.0b2 implements *significant mitigations* to greatly reduce the risk of this denial-of-service vulnerability.  These mitigations **do not** completely eliminate the underlying issue (as that would require changes to GMP itself), but they make successful exploitation *far* more difficult.  The mitigations include:

1.  **Memory Monitoring (`MemoryMonitor` class):**
    *   A new `MemoryMonitor` class is introduced to track estimated memory usage throughout the library's operations.
    *   This class allows setting a maximum memory limit (defaulting to 1024MB, but configurable).
    *   It provides methods to `check_allocation`, `allocate`, and `release` memory, raising a `MemoryError` if an operation would exceed the configured limit.

2.  **Memory Safety Checks (`check_memory_safety` function):**
    *   A new `check_memory_safety` function is used to estimate the memory requirements of various `gmpy2` operations *before* they are executed.
    *   This function considers the operation type (`exp`, `mul`, `pow`, `mod`, `polynomial`, `matrix`, `polynomial_eval`) and the bit lengths of the operands.
    *   It uses conservative estimates and scaling factors to account for `gmpy2`'s internal overhead.
    *   If the estimated memory usage exceeds the limit set by the `MemoryMonitor`, the operation is rejected *before* calling `gmpy2`, preventing the crash.

3.  **Integration into Core Classes:**
    *   The `CyclicGroup` and `FeldmanVSS` classes now use the `check_memory_safety` function before performing potentially memory-intensive operations like `exp`, `mul`, `efficient_multi_exp`, `_evaluate_polynomial`, and `_secure_matrix_solve`.

4.  **Enhanced Input Validation and Error Handling:**
    *  Added improved input validation in functions.
    *  Raises custom exceptions like `SecurityError`, `SerializationError`, `VerificationError`, and `ParameterError` that include detailed information for forensics and debugging.

5.  **Safer Defaults and Configuration:**
    *   The library is configured to use safe primes and large bit lengths by default, reducing the likelihood of accidental misconfiguration leading to excessively large numbers.
    *   The `VSSConfig` class allows users to customize the `prime_bits` and `cache_size`, enabling them to tailor the library to their specific memory constraints.

**Limitations of Mitigations:**

*   **Estimation Inaccuracy:** The `check_memory_safety` function relies on *estimations* of memory usage. While these estimations are conservative, they are not perfect.  It is still theoretically possible (though much less likely) for an operation to consume more memory than estimated, leading to a crash.
*   **GMP Behavior:** The fundamental issue of GMP terminating the process on memory allocation failure remains.  The mitigations prevent most common cases, but a sufficiently determined attacker with knowledge of the estimation algorithm *might* still be able to craft an input that triggers a crash.
*   **Not a Complete Fix:** Version 0.8.0b2 is a *mitigation*, not a complete *elimination* of the vulnerability.

**Workarounds (for versions <= 0.7.6b0):**

If upgrading to version 0.8.0b2 (or later) is not immediately possible, the following workarounds can help reduce the risk:

*   **Limit Input Sizes:**  Carefully restrict the size of inputs to the library, particularly the bit lengths of secrets, shares, and coefficients, and the threshold value (t).  Avoid using excessively large values.  Use the `check_memory_safety` function (available in 0.8.0b2) to manually check the memory usage.
*   **Resource Monitoring:** Implement external monitoring of your application's memory usage.  If memory usage approaches dangerous levels, take action to prevent a crash (e.g., terminate the process, reject new requests, etc.).
*   **Input Validation:** Thoroughly validate all inputs to the library, ensuring they are within expected ranges and of the correct types.
*   **Rate Limiting:** Implement rate limiting to prevent an attacker from flooding your system with requests designed to consume excessive memory.
*  **Custom Memory Allocation**:  *Advanced users* could potentially modify the GMP library to use custom allocation functions that raise Python exceptions instead of terminating the process.  This is a complex and potentially risky approach, and is **not recommended** for most users.  (See [GMP Custom Allocation Documentation](https://gmplib.org/manual/Custom-Allocation)).

**Recommendations:**

*   **Upgrade to 0.8.0b2 (or later) as soon as possible.** This is the *most important* step you can take.
*   **Configure Memory Limits:**  Use the `MemoryMonitor` in 0.8.0b2 (or later) to set appropriate memory limits for your application.  Consider your system's available memory and the expected workload.
*   **Monitor Memory Usage:**  Even with the mitigations, continue to monitor your application's memory usage and be prepared to handle potential memory exhaustion events.
*   **Follow Security Best Practices:**  Implement robust input validation, rate limiting, and other security measures to protect your application from various attacks, not just this specific vulnerability.

**Future Work:**

*   **Rust Integration:**  The long-term solution is to implement the most memory-intensive and security-critical operations in a lower-level language like Rust, which provides more control over memory management and can avoid the problematic GMP behavior. This is planned for future versions.
*   **More Precise Memory Estimation:**  Research and improve the accuracy of the memory estimation algorithms used in `check_memory_safety`.
*   **Fuzz Testing:**  Conduct extensive fuzz testing to identify any remaining edge cases that could trigger excessive memory allocation.

## References
- https://github.com/DavidOsipov/PostQuantum-Feldman-VSS/security/advisories/GHSA-v432-7f47-9g94
- https://github.com/DavidOsipov/PostQuantum-Feldman-VSS
