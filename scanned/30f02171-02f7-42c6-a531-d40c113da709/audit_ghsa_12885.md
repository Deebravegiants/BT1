# [M] Cargo did not verify SSH host keys

## Summary
Severity: Medium
Advisory: GHSA-r5w3-xm58-jv6j
CVE: CVE-2022-46176
CWE: CWE-347
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-r5w3-xm58-jv6j
Type: github-advisory

## Affected
- crates.io: `cargo` — affected >=0 <0.67.1

## Details
The Rust Security Response WG was notified that Cargo did not perform SSH host key verification when cloning indexes and dependencies via SSH. An attacker could exploit this to perform man-in-the-middle (MITM) attacks.

This vulnerability has been assigned CVE-2022-46176.

## Overview

When an SSH client establishes communication with a server, to prevent MITM attacks the client should check whether it already communicated with that server in the past and what the server's public key was back then. If the key changed since the last connection, the connection must be aborted as a MITM attack is likely taking place.

It was discovered that Cargo never implemented such checks, and performed no validation on the server's public key, leaving Cargo users vulnerable to MITM attacks.

## Affected Versions

All Rust versions containing Cargo before 1.66.1 are vulnerable (prior to 0.67.1 for the crates.io package).

Note that even if you don't explicitly use SSH for alternate registry indexes or crate dependencies, you might be affected by this vulnerability if you have configured git to replace HTTPS connections to GitHub with SSH (through git's [`url.<base>.insteadOf`][1] setting), as that'd cause you to clone the crates.io index through SSH.

## Mitigations

We will be releasing Rust 1.66.1 today, 2023-01-10, changing Cargo to check the SSH host key and abort the connection if the server's public key is not already trusted. We recommend everyone to upgrade as soon as possible.

Patch files for Rust 1.66.0 are also available [here][2] for custom-built toolchains.

For the time being Cargo will not ask the user whether to trust a server's public key during the first connection. Instead, Cargo will show an error message detailing how to add that public key to the list of trusted keys. Note that this might break your automated builds if the hosts you clone dependencies or indexes from are not already trusted.

If you can't upgrade to Rust 1.66.1 yet, we recommend configuring Cargo to use the `git` CLI instead of its built-in git support. That way, all git network operations will be performed by the `git` CLI, which is not affected by this vulnerability. You can do so by adding this snippet to your [Cargo configuration file](https://doc.rust-lang.org/cargo/reference/config.html):

```toml
[net]
git-fetch-with-cli = true
```

## Acknowledgments

Thanks to the Julia Security Team for disclosing this to us according to our [security policy][3]!

We also want to thank the members of the Rust project who contributed to fixing this issue. Thanks to Eric Huss and Weihang Lo for writing and reviewing the patch, Pietro Albini for coordinating the disclosure and writing this advisory, and Josh Stone, Josh Triplett and Jacob Finkelman for advising during the disclosure.

[1]: https://git-scm.com/docs/git-config#Documentation/git-config.txt-urlltbasegtinsteadOf
[2]: https://github.com/rust-lang/wg-security-response/tree/main/patches/CVE-2022-46176
[3]: https://www.rust-lang.org/policies/security

## References
- https://github.com/rust-lang/cargo/security/advisories/GHSA-r5w3-xm58-jv6j
- https://nvd.nist.gov/vuln/detail/CVE-2022-46176
- https://git-scm.com/docs/git-config#Documentation/git-config.txt-urlltbasegtinsteadOf
- https://github.com/rust-lang/cargo
- https://github.com/rust-lang/wg-security-response/tree/main/patches/CVE-2022-46176
- https://www.rust-lang.org/policies/security
- http://www.openwall.com/lists/oss-security/2023/11/05/6
