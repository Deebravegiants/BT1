# [H] Improper Input Validation in fruity

## Summary
Severity: High
Advisory: GHSA-h352-g5vw-3926
CVE: CVE-2021-43620
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-16
Source: https://github.com/advisories/GHSA-h352-g5vw-3926
Type: github-advisory

## Affected
- crates.io: `fruity` — affected >=0.1.0 <0.3.0

## Details
Methods of NSString for conversion to a string may return a partial result. Since they call CStr::from_ptr on a pointer to the string buffer, the string is terminated at the first null byte, which might not be the end of the string.

In addition to the vulnerable functions listed for this issue, the implementations of Display, PartialEq, PartialOrd, and ToString for NSString are also affected, since they call those functions.

Since NSString is commonly used as the type for paths by the Foundation framework, null byte truncation might allow for easily bypassing file extension checks. For example, if a file name is provided by a user and validated to have one of a specific set of extensions, with validation taking place before truncation, an attacker can add an accepted extension after a null byte (e.g., file.exe\0.txt). After truncation, the file name used by the application would be file.exe.

It would be better to generate unique names for files, instead of using user-provided names, but not all applications take this approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43620
- https://github.com/nvzqz/fruity/issues/14
- https://github.com/rustsec/advisory-db/pull/1102
- https://github.com/nvzqz/fruity
- https://rustsec.org/advisories/RUSTSEC-2021-0123.html
