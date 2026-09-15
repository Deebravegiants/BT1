# [H] Unpreventable top-level navigation

## Summary
Severity: High
Advisory: GHSA-2q4g-w47c-4674
CVE: CVE-2020-15174
CWE: CWE-20, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2020-10-06
Source: https://github.com/advisories/GHSA-2q4g-w47c-4674
Type: github-advisory

## Affected
- npm: `electron` — affected >=8.0.0-beta.0 <8.5.1
- npm: `electron` — affected >=9.0.0-beta.0 <9.3.0
- npm: `electron` — affected >=10.0.0-beta.0 <10.0.1

## Details
### Impact
The `will-navigate` event that apps use to prevent navigations to unexpected destinations [as per our security recommendations](https://www.electronjs.org/docs/tutorial/security) can be bypassed when a sub-frame performs a top-frame navigation across sites.

### Patches

* `11.0.0-beta.1`
* `10.0.1`
* `9.3.0`
* `8.5.1`

### Workarounds
Sandbox all your iframes using the [`sandbox` attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe#attr-sandbox).  This will prevent them creating top-frame navigations and is good practice anyway.

### For more information
If you have any questions or comments about this advisory:

* Email us at security@electronjs.org

## References
- https://github.com/electron/electron/security/advisories/GHSA-2q4g-w47c-4674
- https://nvd.nist.gov/vuln/detail/CVE-2020-15174
- https://github.com/electron/electron/commit/18613925610ba319da7f497b6deed85ad712c59b
- https://github.com/electron/electron
