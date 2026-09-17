# [M] FacturaScripts Vulnerable to Unauthenticated phpinfo() Disclosure via Installer Endpoint

## Summary
Severity: Medium
Advisory: GHSA-vrxf-vrc4-22p7
CVE: CVE-2026-42878
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-vrxf-vrc4-22p7
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=2026

## Details
### Summary
An unauthenticated information disclosure vulnerability in the Installer controller allows any remote attacker to trigger phpinfo() on a fresh FacturaScripts deployment by requesting /?phpinfo=TRUE, exposing full PHP configuration, server environment variables (including any database credentials, API keys, or application secrets set as env vars), filesystem paths, and loaded extensions without being authenticated.

### Details
The phpinfo() debug endpoint was intentionally added in commit 8c31c106  ("Added phpinfo option to the installer") on February 27, 2018, and has remained in the codebase for over 8 years across multiple major versions.

The feature appears to have been added as a convenience tool to help users diagnose PHP configuration during installation. However, it exposes sensitive server information to any unauthenticated attacker who knows the parameter.

Vulnerable code (Core/Controller/Installer.php ~line 115):

    if ('TRUE' === $this->request->query('phpinfo', '')) {
        phpinfo();
        return;
    }

This vulnerability is of the same class as CVE-2025-34081 (CONPROSYS HMI System unauthenticated phpinfo() exposure), which received a CVE assignment.

Introduced: commit 8c31c1060581ad6ad591c7689da3a8df8a29f486 (Feb 27 2018)
Still present: v2026-39-g262e79208 (confirmed April 2026)

### PoC
Prerequisites: Fresh FacturaScripts deployment where installation has not yet been completed (config.php does not contain db_name).

Step 1 — Clone and serve the application:
    git clone https://github.com/NeoRazorX/facturascripts
    cd facturascripts
    php -S localhost:8000

Step 2 — Send the following unauthenticated GET request:
    GET /?phpinfo=TRUE HTTP/1.1
    Host: localhost:8000

Step 3 — Observe full phpinfo() output returned (20+ pages) containing:
    - Complete PHP configuration
    - All server environment variables
    - Filesystem paths
    - Loaded extensions and versions
    - HTTP request headers

No credentials, cookies, or prior interaction required.

Tested on: PHP 8.1.34, macOS, fresh clone with no configuration applied.
Proof of concept screenshot/PDF available.

### Impact
Vulnerability type: Unauthenticated Information Disclosure (CWE-200)

Any unauthenticated remote attacker who can reach a freshly deployed FacturaScripts instance before installation is completed can retrieve the full PHP environment. On production deployments this includes:

  - Database credentials (DB_PASSWORD, DB_USER) if set as environment variables
  - Application secrets (APP_KEY, JWT secrets) if set as environment variables  
  - Cloud provider credentials (AWS_SECRET_ACCESS_KEY, etc.) if present
  - Full server filesystem paths enabling targeted path traversal attempts
  - Exact PHP version and loaded extensions enabling version-specific attacks
  - All HTTP headers revealing internal infrastructure details
  - Database connection configuration (mysqli default socket, PDO drivers)
  - Exact PHP version enabling version-specific CVE targeting (PHP 8.1.34)

Fresh deployments are commonly left unconfigured for extended periods on shared hosting and cloud environments, making this window reliably exploitable in real-world scenarios.

Fix: Remove lines 115-118 from Core/Controller/Installer.php:

    if ('TRUE' === $this->request->query('phpinfo', '')) {
        phpinfo();
        return;
    }

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-vrxf-vrc4-22p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42878
- https://github.com/NeoRazorX/facturascripts
