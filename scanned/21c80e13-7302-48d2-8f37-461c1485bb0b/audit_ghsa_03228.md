# [M] JWT leak via Open Redirect in Programmatic access

## Summary
Severity: Medium
Advisory: GHSA-35vc-w93w-75c2
CVE: CVE-2021-29651
CWE: CWE-200, CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-05-21
Source: https://github.com/advisories/GHSA-35vc-w93w-75c2
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0 <0.13.4

## Details
### Impact
Using programmatic access on protected sites, one can get a signed login URL with pomerium_redirect_uri set to an arbitrary URL. Then, if the user has already logged into Pomerium, they will be redirected to the specified pomerium_redirect_uri with a JWT attached. This allows an outside attacker to get a signed login URL that, upon visiting it, will redirect a victim to the attacker’s site. This creates an issue of Open Redirect and, more seriously, JWT leakage.

With a leaked JWT, the attacker will be able to unveil the victim’s identity (.e.g. email address) by supplying the JWT to the authenticate service or verify.pomerium.com. In addition, if an application integrating Pomerium only verifies the iss claim and others but not the aud claim, the attacker will be able to access it as the victim.

### Specific Go Packages Affected
github.com/pomerium/pomerium/proxy

### Patches
Patched in Pomerium v0.13.4

### For more information
If you have any questions or comments about this advisory
* Open an issue in [pomerium](http://github.com/pomerium/pomerium)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-35vc-w93w-75c2
- https://nvd.nist.gov/vuln/detail/CVE-2021-29651
- https://github.com/pomerium/pomerium/pull/2049
