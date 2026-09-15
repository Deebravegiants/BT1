# [M] iwasm vulnerable to filesystem sandbox escape with symlink when using uvwasi feature

## Summary
Severity: Medium
Advisory: CVE-2025-43853
Aliases: GHSA-8fc8-4g25-c8m7
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2025-05-15
Source: https://osv.dev/vulnerability/CVE-2025-43853
Type: osv

## Details
The WebAssembly Micro Runtime's (WAMR) iwasm package is the executable binary built with WAMR VMcore which supports WebAssembly System Interface (WASI) and command line interface. Anyone running WAMR up to and including version 2.2.0 or WAMR built with libc-uvwasi on Windows is affected by a symlink following vulnerability. On WAMR running in Windows, creating a symlink pointing outside of the preopened directory and subsequently opening it with create flag will create a file on host outside of the sandbox. If the symlink points to an existing host file, it's also possible to open it and read its content. Version 2.3.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/43xxx/CVE-2025-43853.json
- https://github.com/bytecodealliance/wasm-micro-runtime/security/advisories/GHSA-8fc8-4g25-c8m7
- https://nvd.nist.gov/vuln/detail/CVE-2025-43853
- https://github.com/bytecodealliance/wasm-micro-runtime/commit/28702edaf739cdeee54e81efe5868bf00724c33c
