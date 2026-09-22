# [C] Judge0 vulnerable to Sandbox Escape via Symbolic Link

## Summary
Severity: Critical
Advisory: CVE-2024-28185
Aliases: GHSA-h9g2-45c8-89cf
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-04-18
Source: https://osv.dev/vulnerability/CVE-2024-28185
Type: osv

## Details
Judge0 is an open-source online code execution system. The application does not account for symlinks placed inside the sandbox directory, which can be leveraged by an attacker to write to arbitrary files and gain code execution outside of the sandbox. When executing a submission, Judge0 writes a `run_script` to the sandbox directory. The security issue is that an attacker can create a symbolic link (symlink) at the path `run_script` before this code is executed, resulting in the `f.write` writing to an arbitrary file on the unsandboxed system. An attacker can leverage this vulnerability to overwrite scripts on the system and gain code execution outside of the sandbox.

## References
- https://github.com/judge0/judge0/blob/v1.13.0/app/jobs/isolate_job.rb#L197-L201
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28185.json
- https://github.com/judge0/judge0/security/advisories/GHSA-h9g2-45c8-89cf
- https://nvd.nist.gov/vuln/detail/CVE-2024-28185
- https://github.com/judge0/judge0/commit/846d5839026161bb299b7a35fd3b2afb107992fc
