# [M] Path traversal when MessageBus::Diagnostics is enabled

## Summary
Severity: Medium
Advisory: GHSA-xmgj-5fh3-xjmm
CVE: CVE-2021-43840
CWE: CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-12-17
Source: https://github.com/advisories/GHSA-xmgj-5fh3-xjmm
Type: github-advisory

## Affected
- RubyGems: `message_bus` — affected >=0 <3.3.7

## Details
### Impact

Users who deployed message bus with diagnostics features enabled (default off) were vulnerable to a path traversal bug, which could lead to disclosure of secret information on a machine if an unintended user were to gain access to the diagnostic route. The impact is also greater if there is no proxy for your web application as the number of steps up the directories is not bounded. For deployments which uses a proxy, the impact varies. For example, If a request goes through a proxy like Nginx with `merge_slashes` enabled, the number of steps up the directories that can be read is limited to 3 levels. 

### Patches

Patched in 3.3.7.

### Workarounds

Disable MessageBus::Diagnostics in production like environments.

## References
- https://github.com/discourse/message_bus/security/advisories/GHSA-xmgj-5fh3-xjmm
- https://nvd.nist.gov/vuln/detail/CVE-2021-43840
- https://github.com/discourse/message_bus/commit/9b6deee01ed474c7e9b5ff65a06bb0447b4db2ba
- https://github.com/discourse/message_bus
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/message_bus/CVE-2021-43840.yml
