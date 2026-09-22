# [M] TinyEnv: Missing .env file not required — may cause unexpected behavior

## Summary
Severity: Medium
Advisory: GHSA-3j7m-5g4q-gfpc
CVE: CVE-2025-58758
CWE: CWE-703
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-3j7m-5g4q-gfpc
Type: github-advisory

## Affected
- Packagist: `datahihi1/tiny-env` — affected >=0 <1.0.3
- Packagist: `datahihi1/tiny-env` — affected >=1.0.9 <1.0.11

## Details
### Impact
TinyEnv did not require the `.env` file to exist when loading environment variables.  
This could lead to **unexpected behavior** where the application silently ignores missing configuration, potentially causing insecure defaults or deployment misconfigurations.  

Affected versions:  
- **1.0.1 → 1.0.2**  
- **1.0.9 → 1.0.10**

### Patches
The issue has been fixed in **version 1.0.11**.  
All users should upgrade to `1.0.11` or later.

### Workarounds
As a workaround, users can manually verify the existence of the `.env` file before initializing TinyEnv, for example:

```php
if (!file_exists(__DIR__ . '/.env')) {
    throw new RuntimeException('.env file is missing!');
}

## References
- https://github.com/datahihi1/tiny-env/security/advisories/GHSA-3j7m-5g4q-gfpc
- https://nvd.nist.gov/vuln/detail/CVE-2025-58758
- https://github.com/datahihi1/tiny-env/commit/69b7b885e6cfbf07f470fb3512360e0caa95521e
- https://github.com/datahihi1/tiny-env/commit/7dc656c58bef6050afb8f7a395e38227e31a66df
- https://github.com/datahihi1/tiny-env
