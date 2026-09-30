# [H] Google::Auth versions before 0.09 for Perl allow server side request forgery and credential exfiltration via unvalidated URLs taken from the credentials JSON

## Summary
Severity: High
Advisory: CVE-2026-66901
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-66901
Type: osv

## Details
Google::Auth versions before 0.09 for Perl allow server side request forgery and credential exfiltration via unvalidated URLs taken from the credentials JSON.

The URLs the library requests are read from the credentials JSON, and their hosts were not checked against the universe domain before the request. For an external_account configuration, retrieve_subject_token fetched credential_source.url with headers from the same JSON, and fetch_access_token posted the subject token to token_url, then sent the STS access token it received to service_account_impersonation_url in an Authorization: Bearer header. The authorized_user, impersonated_service_account and service_account configurations posted the client secret and refresh token, the source access token, and a signed JWT assertion to their own JSON-supplied token_uri or impersonation URL.

Any caller that builds credentials from a configuration it does not fully control issues those requests from the application's network position, reaching hosts the configuration names, including internal services and link-local metadata endpoints, and hands them the credentials each request carries. The service_account assertion is bound to aud, so it is not replayable against Google.

Version 0.06 added a _validate_url host check to the external_account class, keyed on a universe_domain read from the same credentials JSON. Version 0.07 gated a JSON-supplied universe domain behind GOOGLE_EXTERNAL_ACCOUNT_ALLOW_CUSTOM_UNIVERSES=1, deriving the pin flag from arguments that an earlier BUILDARGS pass had already merged on the make_creds path. Version 0.08 passed the pin decision through as an explicit constructor argument and moved _validate_url to Google::Auth::Credentials, adding the call to UserRefreshCredentials and ImpersonatedServiceAccountCredentials, and 0.09 added it to ServiceAccountCredentials.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/34
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66901.json
- https://metacpan.org/release/CJCOLLIER/Google-Auth-0.09/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-66901
- https://github.com/GoogleCloudPlatform/google-auth-library-perl/commit/9b5157062acc605ca9e6c507b910587f4829ce9e.patch
- https://github.com/GoogleCloudPlatform/google-auth-library-perl/commit/c95c77e70bec94f17e239d88050f843ea1cade95.patch
- https://github.com/GoogleCloudPlatform/google-auth-library-perl/commit/cbbb07804e3f8cc7cf9638ecc9c2097d80a9ef50.patch
- https://github.com/GoogleCloudPlatform/google-auth-library-perl/commit/cd42bdef53afcc4531161e85e91d0d5997e01324.patch
- https://github.com/GoogleCloudPlatform/google-auth-library-perl
