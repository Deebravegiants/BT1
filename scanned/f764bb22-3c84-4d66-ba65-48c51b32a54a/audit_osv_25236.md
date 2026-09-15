# [C] Sandbox Escape

## Summary
Severity: Critical
Advisory: CVE-2023-32314
Aliases: GHSA-whpj-8f3w-67p5
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-15
Source: https://osv.dev/vulnerability/CVE-2023-32314
Type: osv

## Details
vm2 is a sandbox that can run untrusted code with Node's built-in modules. A sandbox escape vulnerability exists in vm2 for versions up to and including 3.9.17. It abuses an unexpected creation of a host object based on the specification of `Proxy`. As a result a threat actor can bypass the sandbox protections to gain remote code execution rights on the host running the sandbox. This vulnerability was patched in the release of version `3.9.18` of `vm2`. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://gist.github.com/arkark/e9f5cf5782dec8321095be3e52acf5ac
- https://github.com/patriksimek/vm2/releases/tag/3.9.18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32314.json
- https://github.com/patriksimek/vm2/security/advisories/GHSA-whpj-8f3w-67p5
- https://nvd.nist.gov/vuln/detail/CVE-2023-32314
- https://github.com/patriksimek/vm2/commit/d88105f99752305c5b8a77b63ddee3ec86912daf
