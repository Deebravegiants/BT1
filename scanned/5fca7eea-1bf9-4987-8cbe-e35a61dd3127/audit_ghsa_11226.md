# [C] WWBN AVideo is vulnerable to unauthenticated OS Command Injection via base64Url in objects/getImage.php

## Summary
Severity: Critical
Advisory: GHSA-9j26-99jh-v26q
CVE: CVE-2026-29058
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-9j26-99jh-v26q
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <7.0.0

## Details
## Impact

An unauthenticated attacker can execute arbitrary OS commands on the server by injecting shell command substitution into the `base64Url` GET parameter. This can lead to full server compromise, data exfiltration (e.g., configuration secrets, internal keys, credentials), and service disruption.

## Root Cause

The `base64Url` parameter is Base64-decoded and then interpolated directly into a double-quoted `ffmpeg` shell command without proper shell escaping. The upstream validation uses `FILTER_VALIDATE_URL`, which validates URL syntax but does not prevent shell metacharacters / command substitution sequences from being interpreted by the shell.

## Affected Components

* `objects/getImage.php`
* `objects/security.php`
* Execution path via async command execution helper (`shell_exec`/`nohup`)

## Patches

Apply strict shell argument escaping (e.g., `escapeshellarg()`) to all user-supplied values before building any shell command, and avoid double-quoted interpolation of untrusted input. Prefer safer process execution patterns where possible.

## Workarounds

* Restrict access to `objects/getImage.php` at the web server / reverse proxy layer (IP allowlist, auth, or disable endpoint if not needed).
* Apply WAF rules to block suspicious patterns and limit exposure until a patch is deployed.

## Resources

* Report: "Unauthenticated OS Command Injection in AVideo-Encoder"

## References
- https://github.com/WWBN/AVideo-Encoder/security/advisories/GHSA-9j26-99jh-v26q
- https://nvd.nist.gov/vuln/detail/CVE-2026-29058
- https://github.com/WWBN/AVideo-Encoder
