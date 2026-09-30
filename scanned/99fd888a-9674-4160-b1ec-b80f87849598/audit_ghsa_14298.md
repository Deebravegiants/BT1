# [C] vm2 vulnerable to sandbox escape

## Summary
Severity: Critical
Advisory: GHSA-7jxr-cg7f-gpgv
CVE: CVE-2023-29017
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-7jxr-cg7f-gpgv
Type: github-advisory

## Affected
- npm: `vm2` — affected >=0 <3.9.15

## Details
vm2 was not properly handling host objects passed to `Error.prepareStackTrace` in case of unhandled async errors.

- vm2 version: ~3.9.14
- Node version: 18.15.0, 19.8.1, 17.9.1

### Impact
A threat actor can bypass the sandbox protections to gain remote code execution rights on the host running the sandbox.

### Patches
This vulnerability was patched in the release of version `3.9.15` of `vm2`.

### Workarounds
None.

## References
- https://github.com/patriksimek/vm2/security/advisories/GHSA-7jxr-cg7f-gpgv
- https://nvd.nist.gov/vuln/detail/CVE-2023-29017
- https://github.com/patriksimek/vm2/issues/515
- https://github.com/patriksimek/vm2/commit/d534e5785f38307b70d3aac1945260a261a94d50
- https://gist.github.com/seongil-wi/2a44e082001b959bfe304b62121fb76d
- https://github.com/patriksimek/vm2
