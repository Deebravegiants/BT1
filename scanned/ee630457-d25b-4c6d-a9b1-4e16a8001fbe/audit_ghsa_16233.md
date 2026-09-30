# [M] Possible CSRF attack at questionnaire templates preview

## Summary
Severity: Medium
Advisory: GHSA-f3qm-vfc3-jg6v
CVE: CVE-2023-47635
CWE: CWE-352, CWE-918
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-f3qm-vfc3-jg6v
Type: github-advisory

## Affected
- RubyGems: `decidim-templates` — affected >=0.23.0 <0.27.5

## Details
### Impact
The CSRF authenticity token check is currently disabled for the questionnaire templates preview as per:
https://github.com/decidim/decidim/blob/3187bdfd40ea1c57c2c12512b09a7fec0b2bed08/decidim-templates/app/controllers/decidim/templates/admin/questionnaire_templates_controller.rb#L11

This was introduced by this commit in the PR that introduced this feature (#6247):
https://github.com/decidim/decidim/pull/6247/commits/5542227be66e3b6d7530f5b536069bce09376660

The issue does not imply a serious security thread as you need to have access also to the session cookie in order to see this resource. This URL does not allow modifying the resource but it may allow attackers to gain access to information which was not meant to be public.

### Patches
#11743

### Workarounds
Disable the templates functionality or remove all available templates.

### References
#11743

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-f3qm-vfc3-jg6v
- https://nvd.nist.gov/vuln/detail/CVE-2023-47635
- https://github.com/decidim/decidim/pull/11743
- https://github.com/decidim/decidim/pull/6247
- https://github.com/decidim/decidim/commit/5542227be66e3b6d7530f5b536069bce09376660
- https://github.com/decidim/decidim/commit/57a4b467787448307b5d9b01ce6e2c8502e121ac
- https://github.com/decidim/decidim
- https://github.com/decidim/decidim/blob/3187bdfd40ea1c57c2c12512b09a7fec0b2bed08/decidim-templates/app/controllers/decidim/templates/admin/questionnaire_templates_controller.rb#L11
- https://github.com/decidim/decidim/releases/tag/v0.27.5
- https://github.com/decidim/decidim/releases/tag/v0.28.0
