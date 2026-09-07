# [M] Information Disclosure via Flags override link

## Summary
Severity: Medium
Advisory: GHSA-892p-pqrr-hxqr
CVE: CVE-2025-46332
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-02
Source: https://github.com/advisories/GHSA-892p-pqrr-hxqr
Type: github-advisory

## Affected
- npm: `flags` — affected >=0 <4.0.0
- npm: `@vercel/flags` — affected >=0

## Details
## Summary

An information disclosure vulnerability affecting Flags SDK has been addressed. It impacted `flags` ≤3.2.0 and `@vercel/flags` ≤3.1.1 and in certain circumstances, allowed a bad actor with detailed knowledge of the vulnerability to list all flags returned by the flags discovery endpoint (`.well-known/vercel/flags`).

## Impact

This vulnerability allowed for information disclosure, where a bad actor could gain access to a list of all feature flags exposed through the flags discovery endpoint, including the:

- Flag names
- Flag descriptions
- Available options and their labels (e.g. `true`, `false`)
- Default flag values

Not impacted:

- Flags providers were not accessible

No write access nor additional customer data was exposed, this is limited to just the values noted above. Vercel has automatically mitigated this incident on behalf of our customers for the default flags discovery endpoint at `.well-known/vercel/flags`. Flags Explorer will be disabled and show a warning notice until upgraded to `flags@4.0.0`.

## Resolution

The `verifyAccess` function was patched within `flags@4.0.0`. 

Users of `@vercel/flags` should also migrate to `flags@4.0.0`.

For further guidance on upgrading your version, please see our [upgrade guide](https://github.com/vercel/flags/blob/main/packages/flags/guides/upgrade-to-v4.md).

## Mitigations

Vercel implemented a network-level mitigation to prevent the default flags discovery endpoint at `/.well-known/vercel/flags` being reachable, which automatically protects Vercel deployments against exploitation of this issue. Users need to upgrade to `flags@4.0.0` to re-enable the Flags Explorer.

This automatic mitigation is not effective in two scenarios:

- When using the Flags SDK on Pages Router, as the original non-rewritten route would still be accessible, e.g. `/api/vercel/flags`.
- When using a custom path for the flags discovery endpoint.

If you are not protected by the Vercel default mitigation you can temporarily deny access to the other exposed flags discovery endpoints through a custom WAF rule while you upgrade to the latest version.

## References

- https://vercel.com/changelog/information-disclosure-in-flags-sdk-cve-2025-46332
- https://github.com/vercel/flags/blob/main/packages/flags/guides/upgrade-to-v4.md

## References
- https://github.com/vercel/flags/security/advisories/GHSA-892p-pqrr-hxqr
- https://nvd.nist.gov/vuln/detail/CVE-2025-46332
- https://github.com/vercel/flags
- https://github.com/vercel/flags/blob/main/packages/flags/guides/upgrade-to-v4.md
- https://vercel.com/changelog/information-disclosure-in-flags-sdk-cve-2025-46332
