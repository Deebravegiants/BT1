# [M] Decidim: Private exports can be downloaded through reusable links

## Summary
Severity: Medium
Advisory: GHSA-767h-63j4-5226
CVE: CVE-2026-45377
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-767h-63j4-5226
Type: github-advisory

## Affected
- RubyGems: `decidim-core` — affected >=0 <0.30.9
- RubyGems: `decidim-core` — affected >=0.31.0.rc1 <0.31.5
- RubyGems: `decidim-core` — affected >=0.32.0.rc1 <0.32.0

## Details
## Description

The normal `download_your_data` flow requires the requester to be logged in as the export owner, but the resulting Active Storage blob redirect URL can be replayed without authentication by anyone who obtains it.

## Technical description
 
This private export flow turns an authenticated, user-scoped download into a reusable bearer link because the protected Decidim endpoint redirects to the underlying Active Storage blob URL. `Decidim::DownloadYourDataController#download_file` correctly scopes the export record to `current_user`, so the wrapper route itself is not directly accessible to another user. However, once the owner
performs that authenticated GET request, the response redirects to a signed Active Storage URL that is no longer bound to the user session. Anyone who learns that URL can replay it and retrieve the file without being logged in as the export owner.

Because the blob redirect URL is delivered through a GET request and appears in the redirect chain, it is more likely to leak through browser history, logs, proxy tooling, screenshots, copied links, support transcripts, or other client-side handling of URLs.

Reproduction steps:

Step 1. Generate or locate a completed export in the Web UI.
1. Sign in as `user@example.org` at `http://localhost:3001/users/sign_in`.
2. Open `http://localhost:3001/download_your_data`.
3. Request a new export from the page and wait until the export becomes downloadable.
4. Open the completed export entry from the list and copy its wrapper URL, for example `http://localhost:3001/download_your_data/download?uuid=07286e61-932d-46d4-bd74-bcd1340c503f `.

Step 2. Download through the authenticated wrapper route.
1. While still signed in as user@example.org, open the wrapper URL in the browser.
2. Confirm that this Decidim route requires the owner session and is not directly usable when logged out or when logged in as another user.

Step 3. Capture the final bearer URL in the redirect chain.

1. In DevTools Network or Burp, inspect the redirect sequence for the wrapper request.
2. Copy the Active Storage redirect URL, typically matching `http://localhost:3001/rails/active_storage/blobs/redirect/<SIGNED_ID>/<FILENAME>`.
3. Note that the Active Storage redirect URL is no longer protected by the Decidim ownership check.

Step 4. Replay the final file URL without authentication.
1. Open a private window or separate browser with no Decidim session.
2. Paste the copied `http://localhost:3001/rails/active_storage/blobs/redirect/<SIGNED_ID>/<FILENAME>` URL.
3. Confirm the export file still downloads even though you are not logged in as the export owner.

### Impact

Personal data exports can be retrieved through leakage channels such as browser history, logs, referrers, screenshots, copied links, support transcripts, intercepted email content, or other client-side disclosure of the GET URL.

### Patches

See https://github.com/decidim/decidim/pull/16680 

### Workarounds

Disable Private Downloads URLs

### Reference

OWASP A01:2021 Broken Access Control

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-767h-63j4-5226
- https://github.com/decidim/decidim/pull/16680
- https://github.com/decidim/decidim
