# [H] Deno permission escalation vulnerability via open of privileged files with missing `--deny` flag

## Summary
Severity: High
Advisory: GHSA-23rx-c3g5-hv9w
CVE: CVE-2024-34346
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-08
Source: https://github.com/advisories/GHSA-23rx-c3g5-hv9w
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <1.43.1

## Details
The Deno sandbox may be unexpectedly weakened by allowing file read/write access to privileged files in various locations on Unix and Windows platforms. For example, reading `/proc/self/environ` may provide access equivalent to `--allow-env`, and writing `/proc/self/mem` may provide access equivalent to `--allow-all`.

Users who grant read and write access to the entire filesystem may not realize that these access to these files may have additional, unintended consequences. The documentation did not reflect that this practice should be undertaken to increase the strength of the security sandbox. 

### Impact

Users who run code with `--allow-read` or `--allow-write` may unexpectedly end up granting additional permissions via file-system operations.

### Patches

Deno 1.43 and above require explicit `--allow-all` access to read or write `/etc`, `/dev` on unix platform (as well as `/proc` and `/sys` on linux platforms), and any path starting with `\\` on Windows.

### Workarounds

The security sandbox in previous versions of Deno allows for denial of access to these files, but it requires an explicit addition of deny flags: `--deny-read=/dev --deny-read=/sys --deny-read=/proc --deny-read=/etc --deny-write=/dev --deny-write=/sys --deny-write=/proc --deny-write=/etc`. Note that symlinks in allowed locations may defeat this protection in earlier versions of Deno.

### Reporters

This vulnerability was reported by a number of analysts. Thanks to [oliver@secfault-security.com](mailto:oliver@secfault-security.com), [finn@secfault-security.com](mailto:finn@secfault-security.com), @leesh3288, and @cristianstaicu for their reports and analysis.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-23rx-c3g5-hv9w
- https://nvd.nist.gov/vuln/detail/CVE-2024-34346
- https://github.com/denoland/deno
