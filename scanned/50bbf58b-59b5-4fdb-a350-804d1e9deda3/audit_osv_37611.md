# [M] FastGPT Python Sandbox Bypass of File-Write Restriction

## Summary
Severity: Medium
Advisory: CVE-2026-32128
Aliases: GHSA-6hw6-mxrm-v6wj
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-32128
Type: osv

## Details
FastGPT is an AI Agent building platform. In 4.14.7 and earlier, FastGPT's Python Sandbox (fastgpt-sandbox) includes guardrails intended to prevent file writes (static detection + seccomp). These guardrails are bypassable by remapping stdout (fd 1) to an arbitrary writable file descriptor using fcntl. After remapping, writing via sys.stdout.write() still satisfies the seccomp rule write(fd==1), enabling arbitrary file creation/overwrite inside the sandbox container despite the intended no file writes restriction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32128.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-6hw6-mxrm-v6wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32128
