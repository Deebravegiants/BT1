# [M] Insufficient input sanitization in ejson2env 

## Summary
Severity: Medium
Advisory: GHSA-2c47-m757-32g6
CVE: CVE-2025-48069
CWE: CWE-78
Ecosystem: Go, RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-2c47-m757-32g6
Type: github-advisory

## Affected
- Go: `github.com/Shopify/ejson2env/v2` — affected >=0 <2.0.8
- RubyGems: `ejson2env` — affected >=0 <2.0.8
- Go: `github.com/Shopify/ejson2env` — affected >=0

## Details
### Summary
The `ejson2env` tool has a vulnerability related to how it writes to `stdout`. Specifically, the tool is intended to write an export statement for environment variables and their values. However, due to inadequate output sanitization, there is a potential risk where variable names or values may include malicious content, resulting in additional unintended commands being output to `stdout`. If this output is improperly utilized in further command execution, it could lead to command injection vulnerabilities, allowing an attacker to execute arbitrary commands on the host system.

### Details
The vulnerability exists because environment variables are not properly sanitized during the decryption phase, which enables malicious keys or encrypted values to inject commands.

### Impact
An attacker with control over  `.ejson` files can inject commands in the environment where `source $(ejson2env)`  or `eval ejson2env` are executed.


### Mitigation
- Update to a version of `ejson2env` that sanitizes the output during decryption or
- Do not use `ejson2env` to decrypt untrusted user secrets or
- Do not evaluate or execute the direct output from `ejson2env` without removing nonprintable characters.

### Credit
Thanks to security researcher [Demonia](https://hackerone.com/demonia?type=user) for reporting this issue.

## References
- https://github.com/Shopify/ejson2env/security/advisories/GHSA-2c47-m757-32g6
- https://nvd.nist.gov/vuln/detail/CVE-2025-48069
- https://github.com/Shopify/ejson2env/commit/592b3ceea967fee8b064e70983e8cec087b6d840
- https://github.com/Shopify/ejson2env
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/ejson2env/CVE-2025-48069.yml
