# [C] Compromised tag of intercom-php published via GitHub

## Summary
Severity: Critical
Advisory: GHSA-gr3r-crp5-qrrm
CWE: CWE-506
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-gr3r-crp5-qrrm
Type: github-advisory

## Affected
- Packagist: `intercom/intercom-php` — affected 5.0.2

## Details
### Impact

On April 30, 2026, a malicious commit was pushed to the intercom/intercom-php repository and tagged as version 5.0.2, using a compromised service account (github-management-service). This occurred as part of the same supply chain attack that affected intercom-client on npm.

The malicious version contained a Composer plugin that acted as a dropper, downloading the Bun JavaScript runtime (version 1.3.13) and executing an obfuscated credential-harvesting payload. The payload targeted cloud provider credentials (AWS, GCP, Azure), environment variables, .env files, SSH keys, local configuration files, and CI/CD secrets.

The malicious tag was live between approximately 20:53 UTC and 22:37 UTC on April 30, 2026, before being identified and reverted to a clean commit.

This compromise is part of the "Mini Shai-Hulud" supply chain campaign tracked by Wiz and Socket.

To check if a consuming project is affected, run: `composer show intercom/intercom-php --version`. If the project installed or updated between 20:53 and 22:37 UTC on April 30, it may have received the malicious version. The malicious commit hash was `e69bf4b3`. The clean commit is `9371eba9`. Check `composer.lock` to verify which version the consuming project is using.

### Patches

Version 5.0.1 and all prior versions are unaffected. The 5.0.2 tag has been reverted to a clean commit. Downgrade to 5.0.1 or run `composer clear-cache` and reinstall to get the clean 5.0.2.

### Workarounds

If a project installed version 5.0.2 during the affected window, treat all credentials accessible from that environment as compromised and rotate them. Clear the Composer cache with `composer clear-cache` and check `composer.lock` for the commit hash to confirm whether you have the malicious or clean version.

### Resources

- https://www.intercomstatus.com/us-hosting/incidents/01KQFN6VS6ARP1XBR1K1SBYY59
- https://www.wiz.io/blog/mini-shai-hulud-supply-chain-sap-npm

## References
- https://github.com/intercom/intercom-php/security/advisories/GHSA-gr3r-crp5-qrrm
- https://github.com/intercom/intercom-php
- https://www.intercomstatus.com/us-hosting/incidents/01KQFN6VS6ARP1XBR1K1SBYY59
- https://www.wiz.io/blog/mini-shai-hulud-supply-chain-sap-npm
