# [H] CVE-2021-21249

## Summary
Severity: High
Advisory: CVE-2021-21249
Aliases: GHSA-7xhq-m2q9-6hpm
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-15
Source: https://osv.dev/vulnerability/CVE-2021-21249
Type: osv

## Details
OneDev is an all-in-one devops platform. In OneDev before version 4.0.3, there is an issue involving YAML parsing which can lead to post-auth remote code execution. In order to parse and process YAML files, OneDev uses SnakeYaml which by default (when not using `SafeConstructor`) allows the instantiation of arbitrary classes. We can leverage that to run arbitrary code by instantiating classes such as `javax.script.ScriptEngineManager` and using `URLClassLoader` to load the script engine provider, resulting in the instantiation of a user controlled class. For a full example refer to the referenced GHSA. This issue was addressed in 4.0.3 by only allowing certain known classes to be deserialized

## References
- https://github.com/theonedev/onedev/security/advisories/GHSA-7xhq-m2q9-6hpm
- https://github.com/theonedev/onedev/commit/d6fc4212b1ac1e9bbe3ce444e95f9af1e3ab8b66
