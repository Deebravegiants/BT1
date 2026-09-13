# [H] eza Potential Heap Overflow Vulnerability for AArch64

## Summary
Severity: High
Advisory: GHSA-3qx3-6hxr-j2ch
CVE: CVE-2024-25817
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-08
Source: https://github.com/advisories/GHSA-3qx3-6hxr-j2ch
Type: github-advisory

## Affected
- crates.io: `eza` — affected >=0 <0.18.2

## Details
### Summary
In `eza`, there exists a potential heap overflow vulnerability, first seen when using Ubuntu for Raspberry Pi series system, on `ubuntu-raspi` kernel, relating to the `.git` directory.

### Details
The vulnerability seems to be triggered by the `.git` directory in some projects. This issue may be related to specific files, and the directory structure also plays a role in triggering the vulnerability. Files/folders that may be involved in triggering the vulnerability include `.git/HEAD`, `.git/refs`, and `.git/objects`.

As @polly pointed out to me, this is likely caused by [GHSA-j2v7-4f6v-gpg8](https://github.com/libgit2/libgit2/security/advisories/GHSA-j2v7-4f6v-gpg8), which we do seem to use currently.

### PoC
For more information check @CuB3y0nd's blogpost [blog](https://www.cubeyond.net/blog/eza-cve-report).

### Impact
Arbitrary code execution.

## References
- https://github.com/eza-community/eza/security/advisories/GHSA-3qx3-6hxr-j2ch
- https://github.com/eza-community/eza/commit/47c9b90368c49117ba42760bd58acafa3362cbd4
- https://github.com/eza-community/eza
