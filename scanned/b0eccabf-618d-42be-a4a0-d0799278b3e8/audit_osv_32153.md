# [M] Distribution's token authentication allows attacker to inject an untrusted signing key in a JWT

## Summary
Severity: Medium
Advisory: CVE-2025-24976
Aliases: GHSA-phw4-mc57-4hwc, GO-2025-3460
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-02-11
Source: https://osv.dev/vulnerability/CVE-2025-24976
Type: osv

## Details
Distribution is a toolkit to pack, ship, store, and deliver container content. Systems running registry versions 3.0.0-beta.1 through 3.0.0-rc.2 with token authentication enabled may be vulnerable to an issue in which token authentication allows an attacker to inject an untrusted signing key in a JSON web token (JWT). The issue lies in how the JSON web key (JWK) verification is performed. When a JWT contains a JWK header without a certificate chain, the code only checks if the KeyID (`kid`) matches one of the trusted keys, but doesn't verify that the actual key material matches. A fix for the issue is available at commit 5ea9aa028db65ca5665f6af2c20ecf9dc34e5fcd and expected to be a part of version 3.0.0-rc.3. There is no way to work around this issue without patching if the system requires token authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24976.json
- https://github.com/distribution/distribution/security/advisories/GHSA-phw4-mc57-4hwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-24976
- https://github.com/distribution/distribution/commit/f4a500caf68169dccb0b54cb90523e68ee1ac2be
