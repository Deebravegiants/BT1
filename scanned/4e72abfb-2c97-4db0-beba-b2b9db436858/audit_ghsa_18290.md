# [M] astral-tokio-tar has a path traversal in tar extraction

## Summary
Severity: Medium
Advisory: GHSA-3wgq-wrwc-vqmv
CVE: CVE-2025-59825
CWE: CWE-22, CWE-61
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-09-23
Source: https://github.com/advisories/GHSA-3wgq-wrwc-vqmv
Type: github-advisory

## Affected
- crates.io: `astral-tokio-tar` — affected >=0 <0.5.4

## Details
### Impact

In versions 0.5.3 and earlier of astral-tokio-tar, tar archives may extract outside of their intended destination directory when using the `Entry::unpack_in_raw` API. Additionally, the `Entry::allow_external_symlinks` control (which defaults to `true`) could be bypassed via a pair of symlinks that individually point within the destination but combine to point outside of it.

These behaviors could be used individually or combined to bypass the intended security control of limiting extraction to the given directory. This in turn would allow an attacker with a malicious tar archive to perform an arbitrary file write and potentially pivot into code execution (e.g. by overwriting a file that the user or system then executes or uses to execute code). 

The impact of this vulnerability for downstream API users of this crate is **high**, per above. However, for this crate's main downstream user (uv), the impact of this vulnerability is **low** due to its overlap with equivalent user capabilities in source distributions. See GHSA-7j9j-68r2-f35q for additional details.

### Patches

Versions 0.5.4 and newer of astral-tokio-tar address the vulnerability above. Users should upgrade to 0.5.4 or newer.

### Workarounds

Users are advised to upgrade to version 0.5.4 or newer to address this advisory.

There is no workaround other than upgrading.

### References

* See GHSA-7j9j-68r2-f35q for how this vulnerability affects uv, astral-tokio-tar's primary downstream user. Observe that **unlike** this advisory, uv's advisory is considered **low severity** due to overlap with intentional existing capabilities in source distributions.
* This vulnerability is similar to (but not related in code) to CVE-2025-4138 and CVE-2025-4517, which concern Python's tarfile module.

## References
- https://github.com/astral-sh/tokio-tar/security/advisories/GHSA-3wgq-wrwc-vqmv
- https://github.com/google/security-research/security/advisories/GHSA-9p78-p5g6-gcj8
- https://github.com/astral-sh/uv/issues/12163
- https://github.com/astral-sh/tokio-tar/commit/036fdecc85c52458ace92dc9e02e9cef90684e75
- https://github.com/astral-sh/tokio-tar
