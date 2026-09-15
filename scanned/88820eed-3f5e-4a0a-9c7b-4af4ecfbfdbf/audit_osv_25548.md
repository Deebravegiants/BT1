# [H] bjrjk/LinuxASMCallGraph before commit 20dba06 allows attackers to cause a RCE on the server side via uploading a crafted ZIP file due to incorrect filtering rules of uploaded file

## Summary
Severity: High
Advisory: CVE-2023-39346
Aliases: GHSA-63c3-r9qm-c2wx
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-08-04
Source: https://osv.dev/vulnerability/CVE-2023-39346
Type: osv

## Details
LinuxASMCallGraph is software for drawing the call graph of the programming code. Linux ASMCallGraph before commit 20dba06bd1a3cf260612d4f21547c25002121cd5 allows attackers to cause a remote code execution on the server side via uploading a crafted ZIP file due to incorrect filtering rules of uploaded file. The problem has been patched in commit 20dba06bd1a3cf260612d4f21547c25002121cd5. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39346.json
- https://github.com/bjrjk/LinuxASMCallGraph/security/advisories/GHSA-63c3-r9qm-c2wx
- https://nvd.nist.gov/vuln/detail/CVE-2023-39346
- https://github.com/bjrjk/LinuxASMCallGraph/issues/6
- https://github.com/bjrjk/LinuxASMCallGraph/issues/8
- https://github.com/bjrjk/LinuxASMCallGraph/commit/20dba06bd1a3cf260612d4f21547c25002121cd5
