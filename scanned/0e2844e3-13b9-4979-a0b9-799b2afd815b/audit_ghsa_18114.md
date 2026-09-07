# [H] color@5.0.1 contains malware after npm account takeover

## Summary
Severity: High
Advisory: GHSA-qrmh-qg46-72pp
CVE: CVE-2025-59143
CWE: CWE-506
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:A/U:Red (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-qrmh-qg46-72pp
Type: github-advisory

## Affected
- npm: `color` — affected >=5.0.1 <5.0.2

## Details
### Impact
On 8 September 2025, the npm publishing account for `color` was taken over after a phishing attack. Version `5.0.1` was published, functionally identical to the previous patch version, but with a malware payload added attempting to redirect cryptocurrency transactions to the attacker's own addresses from within browser environments.

Local environments, server environments, command line applications, etc. are not affected. If the package was used in a browser context (e.g. a direct `<script>` inclusion, or via a bundling tool such as Babel, Rollup, Vite, Next.js, etc.) there is a chance the malware still exists and such bundles will need to be rebuilt.

The malware seemingly only targets cryptocurrency transactions and wallets such as MetaMask. See references below for more information on the payload.

### Patches
npm removed the offending package from the registry over the course of the day on 8 September, preventing further downloads from npm proper.

On 13 September, the package owner published new patch versions to help cache-bust those using private registries who might still have the compromised version cached. This version is functionally identical to the previously known-good version, published as a patch version bump above the compromised version.

Users should update to the latest patch version, completely remove their `node_modules` directory, clean their package manager's global cache, and rebuild any browser bundles from scratch.

Those operating private registries or registry mirrors should purge the offending versions from any caches.

### References
- https://www.aikido.dev/blog/npm-debug-and-chalk-packages-compromised
- https://socket.dev/blog/npm-author-qix-compromised-in-major-supply-chain-attack
- https://www.ox.security/blog/npm-packages-compromised/

### Point of Contact
In the event suspicious behavior is still observed for the package listed in this security advisory after performing all of the above cleaning operations (see _Patches_ above), please reach out via one of the following channels of communication:

- Bluesky, package owner: https://bsky.app/profile/bad-at-computer.bsky.social
- `debug` repository, tracking issue (applies to all packages affected in the breach): https://github.com/debug-js/debug/issues/1005

## References
- https://github.com/Qix-/color/security/advisories/GHSA-qrmh-qg46-72pp
- https://nvd.nist.gov/vuln/detail/CVE-2025-59143
- https://github.com/debug-js/debug/issues/1005
- https://github.com/Qix-/color
- https://socket.dev/blog/npm-author-qix-compromised-in-major-supply-chain-attack
- https://www.aikido.dev/blog/npm-debug-and-chalk-packages-compromised
- https://www.ox.security/blog/npm-packages-compromised
