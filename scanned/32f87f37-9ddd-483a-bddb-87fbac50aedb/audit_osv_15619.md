# [H] CVE-2019-17664

## Summary
Severity: High
Advisory: CVE-2019-17664
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-16
Source: https://osv.dev/vulnerability/CVE-2019-17664
Type: osv

## Details
NSA Ghidra through 9.0.4 uses a potentially untrusted search path. When executing Ghidra from a given path, the Java process working directory is set to this path. Then, when launching the Python interpreter via the "Ghidra Codebrowser > Window > Python" option, Ghidra will try to execute the cmd.exe program from this working directory.

## References
- https://github.com/NationalSecurityAgency/ghidra/issues/107
