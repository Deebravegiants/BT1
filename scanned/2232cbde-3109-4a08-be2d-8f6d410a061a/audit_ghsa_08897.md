# [M] Grav Vulnerable to Sensitive Information Disclosure via Accounts Service Bypass

## Summary
Severity: Medium
Advisory: GHSA-3f29-pqwf-v4j4
CVE: CVE-2026-42610
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3f29-pqwf-v4j4
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
## Summary
Information disclosure exists in `Grav CMS v1.8.0-beta.29`. Despite previous security patches (notably in `v1.8.0-beta.27/28`) aimed at restricting sensitive object access within the Twig environment, the Accounts Service remains exposed.

A low-privileged user (EX: Content Editor with only pages.update permissions) can bypass the existing Twig sandbox restrictions by utilizing the `grav['accounts']` service. Attacker can programmatically load administrative user objects and extract sensitive data, including Bcrypt password hashes and the security salt.

## Affected version
Grav CMS: `v1.8.0-beta.29` (and earlier 1.8.x beta versions).

Note: This vulnerability persists even after the vendor attempted to mitigate similar SSTI vectors in earlier beta releases.

## Steps to Reproduce
1. Create a low-privileged account (MY CASE IS 'editor_chen') with permissions limited to admin.login and basic page management (create, update, list). Ensure all administrative permissions (Configuration, User Accounts, ...) are explicitly Denied.

2. Login to the Admin panel using  `editor_chen`. Navigate to Pages and edit the `Home` page.


3. Under the Advanced tab, ensure Process Twig is enabled .

4. In the Content tab, inject the following Twig payload designed to bypass the `isDangerousFunction` filter by accessing the internal service container:
```
---
title: Information Disclosure Test
process:
    twig: true
---
# Security Audit Results
- Admin Password Hash: {{ grav['accounts'].load('admin').get('hashed_password') }}
- Security Salt: {{ grav.config.get('security.salt') }}
```
<img width="1176" height="618" alt="GRAV" src="https://github.com/user-attachments/assets/7970216a-2dc6-4d1b-8dfd-b64f3712c9c5" />


5. Click Save. And navigate to the public page (`http://localhost:8000/home`). Page will render and display the administrator's Bcrypt hash and the system security salt.
<img width="1278" height="462" alt="GRAV2" src="https://github.com/user-attachments/assets/33b7b894-6ae3-4d29-bd2d-8004e9b343e0" />







## PoC
```
---
title: Information Disclosure Test
process:
    twig: true
---
# Security Audit Results
- Admin Password Hash: {{ grav['accounts'].load('admin').get('hashed_password') }}
- Security Salt: {{ grav.config.get('security.salt') }}
```

## Impact
Attackers can obtain the password hashes of all registered users, including Super Administrators.

Extracted hashes can be subjected to offline brute-force or dictionary attacks (EX: USE Hashcat)

## Video
Pls refer to the attached video
<video src="https://github.com/user-attachments/assets/74d5ae41-7911-4099-b2cc-e6c51b27c68c" controls="controls" style="max-width: 100%;">
</video>



---

## Maintainer note — fix applied (2026-04-24)

Fixed in Grav core on the `2.0` branch: commit [`d904efc33`](https://github.com/getgrav/grav/commit/d904efc33) — will ship in **2.0.0-beta.2**.

**What changed:** the HMAC key formerly stored as `security.salt` in `user/config/security.yaml` has moved **out of the Config tree** into `user/config/security-private.php`. On upgrade, the existing salt value is migrated into the new file on first request (preserving CSRF nonces and sessions) and the key is scrubbed from both the live `Config` object and the on-disk YAML — so `{{ grav.config.get('security.salt') }}` from a sandboxed Twig template now returns null. The `.php` extension is blocked from web access by the default `user/*.php` htaccess rule; the file contains only a `return` statement, so direct PHP exec produces no output either.

The PoC's password-hash half (`grav['accounts'].load('admin').get('hashed_password')`) was already covered by the new Twig content sandbox in 2.0.0-beta.2 — `UserCollection::load` is not in the sandbox allowlist — see the separate GHSA-58hj-46fw-rcfm advisory.

**Files:**
- [`system/src/Grav/Common/Security.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Security.php) — new `Security::getNonceKey()` + migration.
- [`system/src/Grav/Common/Utils.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Utils.php) — `generateNonceString` now uses the new key.
- [`system/src/Grav/Common/Service/SessionServiceProvider.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Service/SessionServiceProvider.php).
- [`system/src/Grav/Common/Config/Setup.php`](https://github.com/getgrav/grav/blob/2.0/system/src/Grav/Common/Config/Setup.php) — removed auto-gen of `security.salt`.
- [`system/config/security.yaml`](https://github.com/getgrav/grav/blob/2.0/system/config/security.yaml) — removed placeholder `salt:`.
- [`tests/unit/Grav/Common/Security/NonceKeySecurityTest.php`](https://github.com/getgrav/grav/blob/2.0/tests/unit/Grav/Common/Security/NonceKeySecurityTest.php) — migration + generation coverage.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-3f29-pqwf-v4j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42610
- https://github.com/getgrav/grav/commit/c66dfeb5ff679a1667678c6335eb9ff3255dfc47
- https://github.com/getgrav/grav
