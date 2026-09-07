# [M] Umbraco.Cms: Open Redirect Vulnerability in Surface Controllers

## Summary
Severity: Medium
Advisory: GHSA-2qjj-h6wp-c7h7
CVE: CVE-2026-46616
CWE: CWE-601
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-2qjj-h6wp-c7h7
Type: github-advisory

## Affected
- NuGet: `Umbraco.Cms` — affected >=0 <13.14.0
- NuGet: `Umbraco.Cms` — affected >=17.3.0-rc <17.4.0

## Details
### Impact
Some of the Surface Controllers in the CMS provide to support member related operations fail to validate redirect URLs, making Razor templates that derive 'RedirectUrl' from user-controlled query parameters vulnerable to malicious redirect attacks.

### Patches
The issue is resolved in versions 17.4.0 and 13.14.0.

### Workarounds
If users cannot upgrade immediately, they can mitigate the issue in their own site by ensuring every Razor form that posts to `UmbLoginStatusController`, `UmbProfileController` or `UmbRegisterController` passes a concrete, trusted `RedirectUrl` into `Html.BeginUmbracoForm's` route values. 

For example:

```cshtml
  @using (Html.BeginUmbracoForm<UmbLoginStatusController>(
      "HandleLogout",
      new { RedirectUrl = Model.Url() }))
  {
      <button type="submit">Log out</button>
  }
```

### Resources

https://github.com/umbraco/Umbraco-CMS/pull/22565
https://github.com/umbraco/Umbraco-CMS/pull/22561

## References
- https://github.com/umbraco/Umbraco-CMS/security/advisories/GHSA-2qjj-h6wp-c7h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-46616
- https://github.com/umbraco/Umbraco-CMS/pull/22561
- https://github.com/umbraco/Umbraco-CMS/pull/22565
- https://github.com/umbraco/Umbraco-CMS
