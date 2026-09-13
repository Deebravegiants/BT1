# [H] User can manually send request at manager permission to modify system configurations

## Summary
Severity: High
Advisory: CVE-2024-0439
CVSS: 7.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2024-02-25
Source: https://osv.dev/vulnerability/CVE-2024-0439
Type: osv

## Details
As a manager, you should not be able to modify a series of settings. In the UI this is indeed hidden as a convenience for the role since most managers would not be savvy enough to modify these settings. They can use their token to still modify those settings though through a standard HTTP request

While this is not a critical vulnerability, it does indeed need to be patched to enforce the expected permission level.

## References
- https://huntr.com/bounties/7fc1b78e-7faf-4f40-961d-61e53dac81ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0439.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0439
- https://github.com/mintplex-labs/anything-llm/commit/7200a06ef07d92eef5f3c4c8be29824aa001d688
