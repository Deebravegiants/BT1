# [H] Tauri's Updater Private Keys Possibly Leaked via Vite Environment Variables

## Summary
Severity: High
Advisory: GHSA-2rcp-jvr4-r259
CVE: CVE-2023-46115
CWE: CWE-200, CWE-522
Ecosystem: crates.io, npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-2rcp-jvr4-r259
Type: github-advisory

## Affected
- crates.io: `tauri-cli` — affected >=2.0.0-alpha.0 <2.0.0-alpha.16
- npm: `@tauri-apps/cli` — affected >=2.0.0-alpha.0 <2.0.0-alpha.16
- npm: `@tauri-apps/cli` — affected >=1.0.0 <1.5.6
- crates.io: `tauri-cli` — affected >=1.0.0 <1.5.6

## Details
### Impact

This advisory is not describing a vulnerability in the Tauri code base itself but a commonly used misconfiguration which could lead to leaking of the private key and updater key password into bundled Tauri applications using the Vite frontend in a specific configuration.

The Tauri documentation used an insecure example configuration in the [Vite guide](https://tauri.app/v1/guides/getting-started/setup/vite/) to showcase how to use Tauri together with Vite. 

Copying the following snippet `envPrefix: ['VITE_', 'TAURI_'],` from this guide into the `vite.config.ts` of a Tauri project possibly leads to bundling the `TAURI_PRIVATE_KEY` and `TAURI_KEY_PASSWORD` into the Vite frontend code and therefore leaking this value to the debug built of a Tauri application.

The value is automatically bundled into debug builds but for production builds it is not embedded, as long as it is not directly referenced in the frontend code. Vite statically replaces these values in production builds. This reduces the amount of affected applications to a very small amount of affected applications.

To verify if you are affected you can search for the private key value or the `TAURI_PRIVATE_KEY` variable inside the release build frontend assets (`dist/`).

> Example: `grep -r "TAURI_PRIVATE_KEY" dist/`

Using only the `envPrefix: ['VITE_'],` or any other framework than Vite means you are not impacted by this advisory.

### Patches

The documentation has been patched but as the root cause is not in Tauri itself the issue is not fixed by updating Tauri.
The `vite.config.ts` configuration of the project needs to be adapted.

We recommend rotating your updater private key if you are affected by this (requires Tauri CLI >=1.5.5). After updating the envPrefix configuration, generate a new private key with `tauri signer generate`, saving the new private key and updating the updater's `pubkey` value on `tauri.conf.json` with the new public key. To update your existing application, the next application build must be signed with the older private key in order to be accepted by the existing application.

### Workarounds

The `envPrefix: ['VITE_'],`should be used and the desired `TAURI` variables manually added.
Respective these variables could be added `TAURI_PLATFORM`, `TAURI_ARCH`, `TAURI_FAMILY`, `TAURI_PLATFORM_VERSION`, `TAURI_PLATFORM_TYPE` and `TAURI_DEBUG` without leaking sensitive information.

We urge affected users to implement the workaround as the `1.x` branch will not receive a general prevention fix as it would break systems.

### References
The issue was originally disclosed in our discord [here](https://discord.com/channels/616186924390023171/1164260301655523409).
The affected guide is [https://tauri.app/v1/guides/getting-started/setup/vite/](https://tauri.app/v1/guides/getting-started/setup/vite/).


> Update: We lowered the severity from high to low, as the likelihood of impact was found to only affect a **very limited** amount of applications.

> Update2: We changed the affected versions to make clear that after `2.0.0-alpha.16` or `1.5.6` the potentially vulnerable recommendation was no longer visible on our website and should not affect projects by default. A lot of users were confused and we believe this advisory reached the necessary user base.

## References
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-2rcp-jvr4-r259
- https://nvd.nist.gov/vuln/detail/CVE-2023-46115
- https://github.com/tauri-apps/tauri/commit/8b166e9bf82e69ddb3200a3a825614980bd8d433
- https://discord.com/channels/616186924390023171/1164260301655523409
- https://github.com/tauri-apps/tauri
- https://tauri.app/v1/guides/getting-started/setup/vite
