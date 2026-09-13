# [H] @tinacms/cli: Remote Code Execution via Forestry migration — unsanitised __TINA_INTERNAL__ marker in user-controlled YAML labels

## Summary
Severity: High
Advisory: CVE-2026-54074
Aliases: GHSA-4936-9hrh-qqpw
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-54074
Type: osv

## Details
Tina is a headless content management system. @tinacms/cli versions prior to 2.4.3 contain a Remote Code Execution vulnerability in the Forestry-to-Tina migration command. The internal helper addVariablesToCode unquotes any value matching the marker "__TINA_INTERNAL__:::(.*?):::" inside the stringified collection JSON. User-supplied label and name fields from .forestry/**/*.yml are placed into that JSON without any sanitisation. An attacker who controls a Forestry-style project can therefore inject arbitrary JavaScript into the generated tina/templates.{ts,js} file. The injected code is written at module top level, so it executes the moment the developer runs tinacms dev or tinacms build, with the developer's privileges. This issue has been fixed in version 2.4.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54074.json
- https://github.com/tinacms/tinacms/security/advisories/GHSA-4936-9hrh-qqpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-54074
