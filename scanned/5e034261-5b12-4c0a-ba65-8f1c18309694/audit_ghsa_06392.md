# [M] Livewire DOM-based cross-site scripting during client-side state handling

## Summary
Severity: Medium
Advisory: GHSA-g3hc-697w-wm82
CVE: CVE-2026-81887
CWE: CWE-1321, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-g3hc-697w-wm82
Type: github-advisory

## Affected
- Packagist: `livewire/livewire` — affected >=3.0.0-beta.1 <3.8.3
- Packagist: `livewire/livewire` — affected >=4.0.0-beta.1 <4.3.4

## Details
### Impact
In Livewire v3 (≤ 3.8.2) and v4 (≤ 4.3.3), a vulnerability allows unauthenticated attackers to execute arbitrary JavaScript in the origin of an affected application in specific scenarios. The issue stems from how certain client-side component state is handled. This vulnerability does not affect prior major versions. Exploitation requires user interaction, but does not require authentication or prior access to the application. The issue does not bypass server-side authorisation and grants an attacker no privileges beyond those the affected user already holds.

### Patches
This issue has been patched in Livewire v3.8.3 and v4.3.4. All users are strongly encouraged to upgrade to these versions or later as soon as possible.

### Workarounds
There is no known workaround at this time. Users are strongly advised to upgrade to a patched version immediately.

## References
- https://github.com/livewire/livewire/security/advisories/GHSA-g3hc-697w-wm82
- https://nvd.nist.gov/vuln/detail/CVE-2026-81887
- https://github.com/livewire/livewire/pull/10467
- https://github.com/livewire/livewire/commit/11ebe646f7e81dde2d714815da8b3019d058561e
- https://github.com/livewire/livewire
- https://github.com/livewire/livewire/releases/tag/v3.8.3
- https://github.com/livewire/livewire/releases/tag/v4.3.4
