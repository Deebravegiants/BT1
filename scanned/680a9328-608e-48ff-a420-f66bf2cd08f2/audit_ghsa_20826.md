# [M] Cargo extracting malicious crates can fill the file system

## Summary
Severity: Medium
Advisory: GHSA-2hvr-h6gw-qrxp
CVE: CVE-2022-36114
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-2hvr-h6gw-qrxp
Type: github-advisory

## Affected
- crates.io: `cargo` — affected >=0 <0.65.0
- crates.io: `cargo` — affected >=0.66.0 <0.67.0

## Details
The Rust Security Response WG was notified that Cargo did not prevent extracting some malformed packages downloaded from alternate registries. An attacker able to upload packages to an alternate registry could fill the file system when Cargo downloaded the package.

The severity of this vulnerability is "low" for users of alternate registries. Users relying on crates.io are not affected.

Note that **by design** Cargo allows code execution at build time, due to build scripts and procedural macros. The vulnerabilities in this advisory allow performing a subset of the possible damage in a harder to track down way. Your dependencies must still be trusted if you want to be protected from attacks, as it's possible to perform the same attacks with build scripts and procedural macros.

## Disk space exaustion

It was discovered that Cargo did not limit the amount of data extracted from compressed archives. An attacker could upload to an alternate registry a specially crafted package that extracts way more data than its size (also known as a "zip bomb"), exhausting the disk space on the machine using Cargo to download the package.

## Affected versions

The vulnerability is present in all versions of Cargo. Rust 1.64, to be released on September 22nd, will include a fix for it.

Since the vulnerability is just a more limited way to accomplish what a malicious build scripts or procedural macros can do, we decided not to publish Rust point releases backporting the security fix. Patch files are available for Rust 1.63.0 are available [in the wg-security-response repository][patches] for people building their own toolchain.

## Mitigations

We recommend users of alternate registries to excercise care in which package they download, by only including trusted dependencies in their projects. Please note that even with these vulnerabilities fixed, by design Cargo allows arbitrary code execution at build time thanks to build scripts and procedural macros: a malicious dependency will be able to cause damage regardless of these vulnerabilities.

crates.io implemented server-side checks to reject these kinds of packages years ago, and there are no packages on crates.io exploiting these vulnerabilities. crates.io users still need to excercise care in choosing their dependencies though, as the same concerns about build scripts and procedural macros apply here.

## Acknowledgements

We want to thank Ori Hollander from JFrog Security Research for responsibly disclosing this to us according to the [Rust security policy][policy].

We also want to thank Josh Triplett for developing the fixes, Weihang Lo for developing the tests, and Pietro Albini for writing this advisory. The disclosure was coordinated by Pietro Albini and Josh Stone.

[policy]: https://www.rust-lang.org/policies/security
[patches]: https://github.com/rust-lang/wg-security-response/tree/master/patches

## References
- https://github.com/rust-lang/cargo/security/advisories/GHSA-2hvr-h6gw-qrxp
- https://nvd.nist.gov/vuln/detail/CVE-2022-36114
- https://github.com/rust-lang/cargo/commit/2b68d3c07a4a056264dc006ecb9f1354a0679cd3
- https://github.com/rust-lang/cargo/commit/d1f9553c825f6d7481453be8d58d0e7f117988a7
- https://github.com/rust-lang/cargo/commit/d87d57dbbda61754f4fab0f329a7ac520e062c46
- https://github.com/rust-lang/cargo
- https://security.gentoo.org/glsa/202210-09
