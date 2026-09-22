# [H] CVE-2019-13623

## Summary
Severity: High
Advisory: CVE-2019-13623
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13623
Type: osv

## Details
In NSA Ghidra before 9.1, path traversal can occur in RestoreTask.java (from the package ghidra.app.plugin.core.archive) via an archive with an executable file that has an initial ../ in its filename. This allows attackers to overwrite arbitrary files in scenarios where an intermediate analysis result is archived for sharing with other persons. To achieve arbitrary code execution, one approach is to overwrite some critical Ghidra modules, e.g., the decompile module.

## References
- http://packetstormsecurity.com/files/154015/Ghidra-Linux-9.0.4-Arbitrary-Code-Execution.html
- https://ghidra-sre.org/releaseNotes_9.1_final.html
- http://blog.fxiao.me/ghidra/
- https://github.com/NationalSecurityAgency/ghidra/issues/789
