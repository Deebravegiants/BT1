# [H] Sensitive Information leak via Script File in TinaCMS

## Summary
Severity: High
Advisory: GHSA-pc2q-jcxq-rjrr
CVE: CVE-2023-25164
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-pc2q-jcxq-rjrr
Type: github-advisory

## Affected
- npm: `@tinacms/cli` — affected >=1.0.0 <1.0.9

## Details
### Impact

Sensitive Information leaked via script File in TinaCMS. Sites building with @tinacms/cli >= 1.0.0 && < 1.0.9 that store sensitive values in process.env var are impacted. If you're on a version prior to 1.0.0 this vulnerability does not affect you.

If your Tina-enabled website has sensitive credentials stored as environment variables (eg. Algolia API keys) you should rotate those keys immediately.

### Patches

This issue has been patched in @tinacms/cli@1.0.9

### Workarounds

Upgrading, and rotating secure & exposed keys is required for the proper fix.

### References

https://github.com/tinacms/tinacms/pull/3584

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-pc2q-jcxq-rjrr
- https://nvd.nist.gov/vuln/detail/CVE-2023-25164
- https://github.com/tinacms/tinacms/pull/3584
- https://github.com/tinacms/tinacms
