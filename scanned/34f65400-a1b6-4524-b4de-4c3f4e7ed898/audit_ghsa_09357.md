# [C] Compromised version of intercom-client published to npm

## Summary
Severity: Critical
Advisory: GHSA-54pg-9963-v8vg
CWE: CWE-506
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-54pg-9963-v8vg
Type: github-advisory

## Affected
- npm: `intercom-client` — affected 7.0.4

## Details
### Impact

On April 30, 2026, version 7.0.4 of intercom-client was published to npm using credentials obtained from a compromised developer account. This version was not produced by Intercom's build pipeline.

The malicious version contained an obfuscated JavaScript payload that executed during package installation via a preinstall hook. The payload harvested credentials from the environment in which it ran, including cloud provider credentials (AWS, GCP, Azure), environment variables, .env files, GitHub and npm tokens, SSH keys, local configuration files, and cloud metadata service credentials.

Harvested data was exfiltrated to attacker-controlled GitHub repositories. The package was live on npm for approximately 2 hours (15:00-17:00 UTC).

This compromise is part of the "Mini Shai-Hulud" supply chain campaign tracked by Wiz and Socket.

Developers can check if their projects are affected by running: `npm list intercom-client`. If it shows 7.0.4, the project is affected.

### Patches

Version 7.0.3 and all prior versions are unaffected. Downgrade to 7.0.3 immediately.

### Workarounds

If a developer installed version 7.0.4 on any machine or CI system, treat all credentials accessible from that environment as compromised and rotate them. Check lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) for references to 7.0.4. Review CI/CD build logs for any `npm install` that resolved to 7.0.4 between 15:00 and 17:00 UTC on April 30, 2026.

### Resources

- https://socket.dev/blog/intercom-s-npm-package-compromised-in-supply-chain-attack
- https://www.intercomstatus.com/us-hosting/incidents/01KQFN6VS6ARP1XBR1K1SBYY59
- https://www.wiz.io/blog/mini-shai-hulud-supply-chain-sap-npm

## References
- https://github.com/intercom/intercom-node/security/advisories/GHSA-54pg-9963-v8vg
- https://github.com/advisories/GHSA-4594-wxqv-j3pm
- https://github.com/intercom/intercom-node
- https://socket.dev/blog/intercom-s-npm-package-compromised-in-supply-chain-attack
- https://www.intercomstatus.com/us-hosting/incidents/01KQFN6VS6ARP1XBR1K1SBYY59
- https://www.wiz.io/blog/mini-shai-hulud-supply-chain-sap-npm
