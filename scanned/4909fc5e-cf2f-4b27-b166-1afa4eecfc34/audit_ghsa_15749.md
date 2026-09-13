# [M] Decidim vulnerable to data disclosure through the embed feature

## Summary
Severity: Medium
Advisory: GHSA-qcj6-vxwx-4rqv
CVE: CVE-2024-27090
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-qcj6-vxwx-4rqv
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0 <0.27.6

## Details
### Impact

If an attacker can infer the slug or URL of an unpublished or private resource, and this resource can be embedded (such as a Participatory Process, an Assembly, a Proposal, a Result, etc), then some data of this resource could be accessed. 

### Patches

version 0.27.6

https://github.com/decidim/decidim/commit/1756fa639ef393ca8e8bb16221cab2e2e7875705

### Workarounds

Disallow access through your web server to the URLs finished with `/embed.html`

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-qcj6-vxwx-4rqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-27090
- https://github.com/decidim/decidim/pull/12528
- https://github.com/decidim/decidim/commit/1756fa639ef393ca8e8bb16221cab2e2e7875705
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/releases/tag/v0.27.6
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2024-27090.yml
