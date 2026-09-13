# [H] Command injection in Git package in Wrangler

## Summary
Severity: High
Advisory: GHSA-qrg7-hfx7-95c5
CVE: CVE-2022-31249
CWE: CWE-77, CWE-78, CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-25
Source: https://github.com/advisories/GHSA-qrg7-hfx7-95c5
Type: github-advisory

## Affected
- Go: `github.com/rancher/wrangler` — affected >=0 <0.7.4-security1
- Go: `github.com/rancher/wrangler` — affected >=0.8.0 <0.8.5-security1
- Go: `github.com/rancher/wrangler` — affected >=1.0.0 <1.0.1
- Go: `github.com/rancher/wrangler` — affected >=0.8.6 <0.8.11

## Details
### Impact

A command injection vulnerability was discovered in Wrangler's Git package affecting versions up to and including `v1.0.0`.

Wrangler's Git package uses the underlying Git binary present in the host OS or container image to execute Git operations. Specially crafted commands can be passed to Wrangler that will change their behavior and cause confusion when executed through Git, resulting in command injection in the underlying host.

### Workarounds

A workaround is to sanitize input passed to the Git package to remove potential unsafe and ambiguous characters. Otherwise, the best course of action is to update to a patched Wrangler version.

### Patches

Patched versions include `v1.0.1` and later and the backported tags - `v0.7.4-security1`, `v0.8.5-security1` and `v0.8.11`.

### For more information

If you have any questions or comments about this advisory:

* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) or [Wrangler](https://github.com/rancher/wrangler/issues/new) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/wrangler/security/advisories/GHSA-qrg7-hfx7-95c5
- https://nvd.nist.gov/vuln/detail/CVE-2022-31249
- https://github.com/rancher/wrangler/commit/12397eec50155cb2d24aa70bdf9e90c5f3b9a727
- https://github.com/rancher/wrangler/commit/341018c8fef3e12867c7cb2649bd2cecac75f287
- https://github.com/rancher/wrangler/commit/5a387e13e8d51e3340d9e5012a1951f0cca5fc90
- https://github.com/rancher/wrangler/commit/8649ecc062204f28764fd80157a621cbae89c9cf
- https://bugzilla.suse.com/show_bug.cgi?id=1200299
- https://github.com/advisories/GHSA-qrg7-hfx7-95c5
- https://github.com/rancher/wrangler
- https://github.com/rancher/wrangler/compare/v0.7.2...v0.7.4-security1
- https://github.com/rancher/wrangler/compare/v0.8.4...v0.8.5-security1
- https://pkg.go.dev/vuln/GO-2023-1519
