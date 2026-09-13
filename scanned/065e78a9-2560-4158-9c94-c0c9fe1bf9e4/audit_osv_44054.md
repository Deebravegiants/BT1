# [M] RansomLook Arbitrary File Read via Path Traversal in Post screen Field

## Summary
Severity: Medium
Advisory: CVE-2026-78381
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78381
Type: osv

## Details
RansomLook contains a path traversal vulnerability in the handling of the screen field associated with group posts. The GroupPost.get API handler concatenates the database-controlled screen value directly with the application's source/ directory and opens the resulting path without verifying that the resolved file remains within the intended directory.

Because the screen field is free-form and can be populated either through the administrative post editor or through data imported from a remote RansomLook instance, a malicious upstream instance can provide traversal sequences such as ../config/generic.json. When the affected post is subsequently retrieved through the API, RansomLook resolves and reads the attacker-controlled path and returns the contents of the referenced file Base64-encoded in the API response.

This can allow an attacker (being admin) controlling imported post data to read arbitrary files accessible to the RansomLook process, potentially exposing sensitive configuration data, API credentials, password hashes, or other application secrets. The attack does not require the malicious upstream to possess an account on the affected RansomLook instance.

The vulnerability is addressed by resolving screen paths with os.path.realpath() and verifying that the resolved path remains beneath the application's source/ directory. Validation is performed both when values are written and immediately before files are read. Using canonical paths also prevents traversal through symbolic links that would bypass purely lexical path normalization checks.

## References
- https://github.com/RansomLook/RansomLook/c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78381.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78381
- https://github.com/RansomLook/RansomLook/commit/274faccf65898e88ef54f35f304e0821a852a0b8
