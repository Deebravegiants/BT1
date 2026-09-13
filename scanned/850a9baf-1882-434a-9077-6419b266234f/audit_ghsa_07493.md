# [H] MantisBT: Remote Code Execution via eval() Class Hoisting in adm_config_set.php

## Summary
Severity: High
Advisory: GHSA-v84x-qvhg-f36r
CVE: CVE-2026-49273
CWE: CWE-95
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-v84x-qvhg-f36r
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=1.3.0 <2.28.4

## Details
MantisBT 2.28.3 and earlier contains a remote code execution vulnerability in the admin "Manage Configuration" feature (adm_config_set.php). When setting a configuration value with a non-string type (integer, float, complex), the value is passed through ConfigParser -> Tokenizer, which calls *eval()* with a `return;` prefix intended to prevent code execution.

However, PHP hoists function and class declarations at compile time, even past a *return* statement. An attacker can define a class in the eval()'d code that hijacks a class loaded later via PHP's autoloader, achieving arbitrary code execution.

This vulnerability requires administrator access to the web UI (adm_config_set.php). The REST API's ConfigsSetCommand does NOT use Tokenizer/eval() and is not affected.

### Impact
- Remote code execution as the web server user (www-data) from an authenticated administrator session

### Patches
- https://github.com/mantisbt/mantisbt/commit/78c0af63d1fe0118004744cab21ca3bf2cea0f5c

### Workarounds
None. 

### Resources
- https://mantisbt.org/bugs/view.php?id=37122

### Credits
McCaulay Hudson (@_McCaulay) of watchTowr

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-v84x-qvhg-f36r
- https://github.com/mantisbt/mantisbt/commit/78c0af63d1fe0118004744cab21ca3bf2cea0f5c
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37122
