# [M] AlchemyCMS has Authenticated Remote Code Execution (RCE) via eval injection in ResourcesHelper

## Summary
Severity: Medium
Advisory: CVE-2026-23885
Aliases: GHSA-2762-657x-v979
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23885
Type: osv

## Details
Alchemy is an open source content management system engine written in Ruby on Rails. Prior to versions 7.4.12 and 8.0.3, the application uses the Ruby `eval()` function to dynamically execute a string provided by the `resource_handler.engine_name` attribute in `Alchemy::ResourcesHelper#resource_url_proxy`. The vulnerability exists in `app/helpers/alchemy/resources_helper.rb` at line 28. The code explicitly bypasses security linting with `# rubocop:disable Security/Eval`, indicating that the use of a dangerous function was known but not properly mitigated. Since `engine_name` is sourced from module definitions that can be influenced by administrative configurations, it allows an authenticated attacker to escape the Ruby sandbox and execute arbitrary system commands on the host OS. Versions 7.4.12 and 8.0.3 fix the issue by replacing `eval()` with `send()`.

## References
- https://github.com/AlchemyCMS/alchemy_cms/releases/tag/v7.4.12
- https://github.com/AlchemyCMS/alchemy_cms/releases/tag/v8.0.3
- https://github.com/AlchemyCMS/alchemy_cms/security/advisories/GHSA-2762-657x-v979
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23885.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23885
- https://github.com/AlchemyCMS/alchemy_cms/commit/55d03ec600fd9e07faae1138b923790028917d26
- https://github.com/AlchemyCMS/alchemy_cms/commit/563c4ce45bf5813b7823bf3403ca1fc32cb769e7
