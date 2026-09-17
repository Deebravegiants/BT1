# [H] GZDoom engine allows arbitrary code execution via ZScript actor states

## Summary
Severity: High
Advisory: CVE-2025-54065
Aliases: GHSA-prhc-chfw-32jg
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2025-12-03
Source: https://osv.dev/vulnerability/CVE-2025-54065
Type: osv

## Details
GZDoom is a feature centric port for all Doom engine games. GZDoom is an open source Doom engine. In versions 4.14.2 and earlier, ZScript actor state handling allows scripts to read arbitrary addresses, write constants into the JIT-compiled code section, and redirect control flow through crafted FState and VMFunction structures. A script can copy FState structures into a writable buffer, modify function pointers and state transitions, and cause execution of attacker-controlled bytecode, leading to arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54065.json
- https://github.com/ZDoom/gzdoom/security/advisories/GHSA-prhc-chfw-32jg
- https://nvd.nist.gov/vuln/detail/CVE-2025-54065
