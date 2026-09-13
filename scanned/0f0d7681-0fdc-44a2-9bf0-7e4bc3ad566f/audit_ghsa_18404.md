# [C] Livewire is vulnerable to remote command execution during component property update hydration

## Summary
Severity: Critical
Advisory: GHSA-29cq-5w36-x7w3
CVE: CVE-2025-54068
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-17
Source: https://github.com/advisories/GHSA-29cq-5w36-x7w3
Type: github-advisory

## Affected
- Packagist: `livewire/livewire` — affected >=3.0.0-beta.1 <3.6.4

## Details
### Impact
In Livewire v3 (≤ 3.6.3), a vulnerability allows unauthenticated attackers to achieve remote command execution in specific scenarios. The issue stems from how certain component property updates are hydrated. This vulnerability is unique to Livewire v3 and does not affect prior major versions. Exploitation requires a component to be mounted and configured in a particular way, but does not require authentication or user interaction.

### Patches
This issue has been patched in Livewire v3.6.4. All users are strongly encouraged to upgrade to this version or later as soon as possible.

### Workarounds
There is no known workaround at this time. Users are strongly advised to upgrade to a patched version immediately.

### Resources
No public references available at this time to avoid exposure. Details will be published after a responsible disclosure window.

## References
- https://github.com/livewire/livewire/security/advisories/GHSA-29cq-5w36-x7w3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54068
- https://github.com/livewire/livewire/commit/ef04be759da41b14d2d129e670533180a44987dc
- https://github.com/livewire/livewire
- https://github.com/livewire/livewire/releases/tag/v3.6.4
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-54068
- https://www.threathunter.ai/blog/iranian-threat-actor-tools-techniques-iocs-ioas
