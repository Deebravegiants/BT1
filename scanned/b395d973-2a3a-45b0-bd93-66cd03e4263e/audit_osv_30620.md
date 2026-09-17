# [H] Rizin has a command injection via RzBinInfo bclass due legacy code

## Summary
Severity: High
Advisory: CVE-2024-53256
Aliases: GHSA-5jhc-frm4-p8v9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-23
Source: https://osv.dev/vulnerability/CVE-2024-53256
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. `rizin.c` still had an old snippet of code which suffered a command injection due the usage of `rz_core_cmdf` to invoke the command `m` which was removed in v0.1.x. A malicious binary defining `bclass` (part of RzBinInfo) is executed if `rclass` (part of RzBinInfo) is set to `fs`; the vulnerability can be exploited by any bin format where `bclass` and `rclass` are user defined. This vulnerability is fixed in 0.7.4.

## References
- https://github.com/rizinorg/rizin/blob/be24ca8879ed9c58f288bdf21c271b6294720da4/librz/main/rizin.c#L1275-L1278
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53256.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-5jhc-frm4-p8v9
- https://nvd.nist.gov/vuln/detail/CVE-2024-53256
- https://github.com/rizinorg/rizin/commit/db6c5b39c065ce719f587c9815c47fbb834b10fa
