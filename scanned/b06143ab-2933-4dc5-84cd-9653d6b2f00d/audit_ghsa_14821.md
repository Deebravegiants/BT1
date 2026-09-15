# [M] Improper Handling of Insufficient Permissions in `wagtail.contrib.settings`

## Summary
Severity: Medium
Advisory: GHSA-xxfm-vmcf-g33f
CVE: CVE-2024-35228
CWE: CWE-280
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-xxfm-vmcf-g33f
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=6.0.0 <6.0.5
- PyPI: `wagtail` — affected >=6.1.0 <6.1.2

## Details
### Impact
Due to an improperly applied permission check in the `wagtail.contrib.settings` module, a user with access to the Wagtail admin and knowledge of the URL of the edit view for a settings model can access and update that setting, even when they have not been granted permission over the model. The vulnerability is not exploitable by an ordinary site visitor without access to the Wagtail admin.

### Patches
Patched versions have been released as Wagtail 6.0.5 and 6.1.2. Wagtail releases prior to 6.0 are unaffected.

### Workarounds

No workaround is available.

### Acknowledgements

Many thanks to Victor Miti for reporting this issue.

### For more information
If you have any questions or comments about this advisory:

* Visit Wagtail's [support channels](https://docs.wagtail.io/en/stable/support.html)
* Email us at [security@wagtail.org](mailto:security@wagtail.org) (view our [security policy](https://github.com/wagtail/wagtail/security/policy) for more information).

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-xxfm-vmcf-g33f
- https://nvd.nist.gov/vuln/detail/CVE-2024-35228
- https://github.com/wagtail/wagtail/commit/284f75a6f91f7ab18cc304d7d34f33b559ae37b1
- https://github.com/wagtail/wagtail
