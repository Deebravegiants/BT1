# [C] Sandbox Escape in vm2

## Summary
Severity: Critical
Advisory: CVE-2023-30547
Aliases: GHSA-ch3r-j5x3-6q2m
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-17
Source: https://osv.dev/vulnerability/CVE-2023-30547
Type: osv

## Details
vm2 is a sandbox that can run untrusted code with whitelisted Node's built-in modules. There exists a vulnerability in exception sanitization of vm2 for versions up to 3.9.16, allowing attackers to raise an unsanitized host exception inside `handleException()` which can be used to escape the sandbox and run arbitrary code in host context. This vulnerability was patched in the release of version `3.9.17` of `vm2`. There are no known workarounds for this vulnerability. Users are advised to upgrade.

## References
- https://gist.github.com/leesh3288/381b230b04936dd4d74aaf90cc8bb244
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30547.json
- https://github.com/patriksimek/vm2/security/advisories/GHSA-ch3r-j5x3-6q2m
- https://nvd.nist.gov/vuln/detail/CVE-2023-30547
- https://github.com/patriksimek/vm2/commit/4b22e87b102d97d45d112a0931dba1aef7eea049
- https://github.com/patriksimek/vm2/commit/f3db4dee4d76b19869df05ba7880d638a880edd5
