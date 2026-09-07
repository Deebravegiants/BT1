# [M] Potential for cross-site scripting in PostHog-js

## Summary
Severity: Medium
Advisory: GHSA-8775-5hwv-wr6v
CVE: CVE-2023-32325
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-8775-5hwv-wr6v
Type: github-advisory

## Affected
- npm: `posthog-js` — affected >=0 <1.57.2

## Details
### Impact

Potential for cross-site scripting in `posthog-js`.

### Patches

The problem has been patched in `posthog-js` version 1.57.2.

### Workarounds

- This isn't an issue for sites that have a Content Security Policy in place.
- Using the HTML tracking snippet on PostHog Cloud always guarantees the latest version of the library – in that case no action is required to upgrade to the patched version.

### References

We will publish details of the vulnerability in 30 days as per our [security policy](https://posthog.com/handbook/company/security#policies).

## References
- https://github.com/PostHog/posthog-js/security/advisories/GHSA-8775-5hwv-wr6v
- https://nvd.nist.gov/vuln/detail/CVE-2023-32325
- https://github.com/PostHog/posthog-js/pull/630
- https://github.com/PostHog/posthog-js/commit/67e07eb8bb271a3a6f4aa251382e4d25abb385a0
- https://github.com/PostHog/posthog-js
