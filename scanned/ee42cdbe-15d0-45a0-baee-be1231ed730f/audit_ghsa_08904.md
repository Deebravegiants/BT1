# [C] Grav has multiple RCE vectors: unsafe unserialize (x3), command injection in git clone, SSTI blocklist bypass

## Summary
Severity: Critical
Advisory: GHSA-vj3m-2g9h-vm4p
CWE: CWE-502, CWE-78
Ecosystem: Packagist
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-vj3m-2g9h-vm4p
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
Multiple RCE vectors were found in Grav CMS. Three are critical, two are high.

**1. Unsafe unserialize() in JobQueue — direct RCE gadget (Critical)**

`system/src/Grav/Common/Scheduler/JobQueue.php:465` calls `unserialize(base64_decode(...))` without restricting `allowed_classes`. The `Job` class has `call_user_func_array($this->command, $this->args)` in its execution path, which is a direct gadget chain — inject a serialized `Job` with `command = 'system'` and `args = ['whoami']`.

The same codebase actually has a `Serializable` trait that correctly restricts classes, so this inconsistency stands out.

**2. Unsafe unserialize() in FileCache — arbitrary class instantiation (Critical)**

`system/src/Grav/Framework/Cache/Adapter/FileCache.php:75` does `unserialize($value, ['allowed_classes' => true])`. That `true` allows instantiation of any class. If an attacker can write to the cache directory (via any file write primitive), they get object injection → RCE.

**3. Unsafe unserialize() in Session (High)**

`system/src/Grav/Common/Session.php:116` — same `allowed_classes => true` pattern on session data. Lower severity since session storage is typically more restricted.

**4. Command injection in git clone (Critical)**

`system/src/Grav/Console/Cli/InstallCommand.php:150` — only `$this->destination` uses `escapeshellarg()`. The `$data['branch']`, `$data['url']`, and `$data['path']` variables go directly into the shell command without escaping. Admin-accessible via plugin/theme installation.

**5. SSTI blocklist bypass (High)**

`system/src/Grav/Common/Security.php:267-286` — `cleanDangerousTwig()` blocks `twig_array_map` and `twig_array_filter` but not `twig_array_reduce`. Also missing `file_get_contents` and `fwrite` from the dangerous function blocklist. An attacker who can inject Twig templates can bypass the security filter.

All five are independently exploitable. The unserialize issues are the most concerning since they don't require admin access if there's any file write primitive.

— ProScan AppSec | proscan.one


---

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`c66dfeb5f`](https://github.com/getgrav/grav/commit/c66dfeb5f) (items #1, #2, #3, #4) and commit [`38685ac25`](https://github.com/getgrav/grav/commit/38685ac25) + [`c66dfeb5f`](https://github.com/getgrav/grav/commit/c66dfeb5f) (item #5) — ships in **2.0.0-beta.2**.

All five vectors addressed:

1. **Scheduler\JobQueue unsafe unserialize** — `serialized_job` now carries a sibling `serialized_job_hmac` signed with `Security::getNonceKey()`. `reconstructJob` refuses to unserialize an item whose HMAC is missing/mismatched and falls through to the safe structured-fields rebuild. A tampered queue file can no longer smuggle a forged `Job` for direct RCE via `Job::exec → call_user_func_array`.  
   → [`system/src/Grav/Common/Scheduler/JobQueue.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Scheduler/JobQueue.php)

2. **FileCache unsafe unserialize** — same HMAC-integrity approach; see separate GHSA-gwfr-jfjf-92vv.  
   → [`system/src/Grav/Framework/Cache/Adapter/FileCache.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Framework/Cache/Adapter/FileCache.php)

3. **Session::getFlashObject unsafe unserialize** — payload now wrapped in a `v2|<hmac>|<serialized>` envelope; legacy/forged envelopes return null instead of triggering `unserialize`.  
   → [`system/src/Grav/Common/Session.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Session.php)

4. **InstallCommand `git clone` shell injection** — `branch`, `url`, and `path` values read from `user/.dependencies` are now passed through `escapeshellarg`, with a `--` separator before url/path to block option-injection (e.g. `--upload-pack=evil`).  
   → [`system/src/Grav/Console/Cli/InstallCommand.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Console/Cli/InstallCommand.php)

5. **SSTI blocklist bypass** — `twig_array_reduce` (the specific name called out) plus `twig_array_some` and `twig_array_every` added to `cleanDangerousTwig`'s `CALLABLE_DANGEROUS_NAMES` alongside the existing `twig_array_map`/`filter`. More importantly, the new Twig content sandbox in 2.0.0-beta.2 blocks this class of attack at a different layer — see the sandbox work in [`38685ac25`](https://github.com/getgrav/grav/commit/38685ac25).  
   → [`system/src/Grav/Common/Security.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Security.php)

**Tests:**
- [`tests/unit/Grav/Common/Security/UnserializeIntegritySecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/UnserializeIntegritySecurityTest.php) — 8 cases covering JobQueue + Session HMAC integrity.
- [`tests/unit/Grav/Common/Security/FileCacheSecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/FileCacheSecurityTest.php).
- [`tests/unit/Grav/Common/Security/CleanDangerousTwigTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/CleanDangerousTwigTest.php) — new `twig_array_*` entries in `providerCallbackFunctions`.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-vj3m-2g9h-vm4p
- https://github.com/getgrav/grav/commit/5a12f9be8314682c8713e569e330f11805d0a663
- https://github.com/getgrav/grav
