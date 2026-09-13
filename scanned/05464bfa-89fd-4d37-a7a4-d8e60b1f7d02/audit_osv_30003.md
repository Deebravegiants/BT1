# [C] Lack of Input Validation in RDS Light - Potential for Injection Attacks and Memory Tampering

## Summary
Severity: Critical
Advisory: CVE-2024-48918
Aliases: GHSA-5f6w-8mqh-hv2g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-48918
Type: osv

## Details
RDS Light is a simplified version of the Reflective Dialogue System (RDS), a self-reflecting AI framework. Versions prior to 1.1.0 contain a vulnerability that involves a lack of input validation within the RDS AI framework, specifically within the user input handling code in the main module (`main.py`). This leaves the framework open to injection attacks and potential memory tampering. Any user or external actor providing input to the system could exploit this vulnerability to inject malicious commands, corrupt stored data, or affect API calls. This is particularly critical for users employing RDS AI in production environments where it interacts with sensitive systems, performs dynamic memory caching, or retrieves user-specific data for analysis. Impacted areas include developers using the RDS AI system as a backend for AI-driven applications and systems running RDS AI that may be exposed to untrusted environments or receive unverified user inputs. The vulnerability has been patched in version 1.1.0 of the RDS AI framework. All user inputs are now sanitized and validated against a set of rules designed to mitigate malicious content. Users should upgrade to version 1.1.0 or higher and ensure all dependencies are updated to their latest versions. For users unable to upgrade to the patched version, a workaround can be implemented. The user implementing the workaround should implement custom validation checks for user inputs to filter out unsafe characters and patterns (e.g., SQL injection attempts, script injections) and limit or remove features that allow user input until the system can be patched.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48918.json
- https://github.com/RDSaiPlatforms/RDSlight/commit/7dac0e214a344447a2a8ea7414188c38c6a61a6e
- https://github.com/RDSaiPlatforms/RDSlight/security/advisories/GHSA-5f6w-8mqh-hv2g
- https://nvd.nist.gov/vuln/detail/CVE-2024-48918
