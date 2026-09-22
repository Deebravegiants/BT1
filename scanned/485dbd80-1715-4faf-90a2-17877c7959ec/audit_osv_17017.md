# [M] CVE-2020-11104

## Summary
Severity: Medium
Advisory: CVE-2020-11104
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-03-30
Source: https://osv.dev/vulnerability/CVE-2020-11104
Type: osv

## Details
An issue was discovered in USC iLab cereal through 1.3.0. Serialization of an (initialized) C/C++ long double variable into a BinaryArchive or PortableBinaryArchive leaks several bytes of stack or heap memory, from which sensitive information (such as memory layout or private keys) can be gleaned if the archive is distributed outside of a trusted context.

## References
- https://github.com/USCiLab/cereal/issues/625
