# [M] CVE-2025-5702

## Summary
Severity: Medium
Advisory: CVE-2025-5702
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-06-05
Source: https://osv.dev/vulnerability/CVE-2025-5702
Type: osv

## Details
The strcmp implementation optimized for the Power10 processor in the GNU C Library version 2.39 and later writes to vector registers v20 to v31 without saving contents from the caller (those registers are defined as non-volatile registers by the powerpc64le ABI), resulting in overwriting of its contents and potentially altering control flow of the caller, or leaking the input strings to the function to other parts of the program.

## References
- https://sourceware.org/bugzilla/show_bug.cgi?id=33056
