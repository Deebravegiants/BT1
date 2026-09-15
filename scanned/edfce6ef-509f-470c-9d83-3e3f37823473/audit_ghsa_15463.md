# [H] Tina search token leak via lock file in TinaCMS

## Summary
Severity: High
Advisory: GHSA-4qrm-9h4r-v2fx
CVE: CVE-2024-45391
CWE: CWE-200, CWE-312
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-03
Source: https://github.com/advisories/GHSA-4qrm-9h4r-v2fx
Type: github-advisory

## Affected
- npm: `@tinacms/cli` — affected >=0 <1.6.2

## Details
### Impact
Tina search token leaked via lock file (tina-lock.json) in TinaCMS. Sites building with @tinacms/cli < 1.6.2 that use a search token are impacted.

If your Tina-enabled website has search setup, you should rotate that key immediately.

### Patches
This issue has been patched in @tinacms/cli@1.6.2

### Workarounds
Upgrading, and rotating search token is required for the proper fix.

### References
https://github.com/tinacms/tinacms/pull/4758

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-4qrm-9h4r-v2fx
- https://nvd.nist.gov/vuln/detail/CVE-2024-45391
- https://github.com/tinacms/tinacms/pull/4758
- https://github.com/tinacms/tinacms/commit/110f1ceea4574d636a64526648f7c8bf6539b26a
- https://github.com/tinacms/tinacms
