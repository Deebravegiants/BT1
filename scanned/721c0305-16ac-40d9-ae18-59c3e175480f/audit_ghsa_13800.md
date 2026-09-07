# [M] CarrierWave Content-Type allowlist bypass vulnerability, possibly leading to XSS

## Summary
Severity: Medium
Advisory: GHSA-gxhx-g4fq-49hj
CVE: CVE-2023-49090
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-29
Source: https://github.com/advisories/GHSA-gxhx-g4fq-49hj
Type: github-advisory

## Affected
- RubyGems: `carrierwave` — affected >=3.0.0 <3.0.5
- RubyGems: `carrierwave` — affected >=0 <2.2.5

## Details
### Impact
[CarrierWave::Uploader::ContentTypeAllowlist](https://github.com/carrierwaveuploader/carrierwave/blob/master/lib/carrierwave/uploader/content_type_allowlist.rb) has a Content-Type allowlist bypass vulnerability, possibly leading to XSS. 

The validation in `allowlisted_content_type?` determines Content-Type permissions by performing a partial match.
If the `content_type` argument of `allowlisted_content_type?` is passed a value crafted by the attacker, Content-Types not included in the `content_type_allowlist` will be allowed.

In addition, by setting the Content-Type configured by the attacker at the time of file delivery, it is possible to cause XSS on the user's browser when the uploaded file is opened.

### Patches
Upgrade to [3.0.5](https://rubygems.org/gems/carrierwave/versions/3.0.5) or [2.2.5](https://rubygems.org/gems/carrierwave/versions/2.2.5).

### Workarounds
When validating with `allowlisted_content_type?` in [CarrierWave::Uploader::ContentTypeAllowlist](https://github.com/carrierwaveuploader/carrierwave/blob/master/lib/carrierwave/uploader/content_type_allowlist.rb) , forward match(`\A`) the Content-Type set in `content_type_allowlist`, preventing unintentional permission of `text/html;image/png` when you want to allow only `image/png` in `content_type_allowlist`.

### References
[OWASP - File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html#content-type-validation)

## References
- https://github.com/carrierwaveuploader/carrierwave/security/advisories/GHSA-gxhx-g4fq-49hj
- https://nvd.nist.gov/vuln/detail/CVE-2023-49090
- https://github.com/carrierwaveuploader/carrierwave/commit/39b282db5c1303899b3d3381ce8a837840f983b5
- https://github.com/carrierwaveuploader/carrierwave/commit/863d425c76eba12c3294227b39018f6b2dccbbf3
- https://github.com/carrierwaveuploader/carrierwave
- https://github.com/carrierwaveuploader/carrierwave/blob/master/lib/carrierwave/uploader/content_type_allowlist.rb
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/carrierwave/CVE-2023-49090.yml
- https://rubygems.org/gems/carrierwave/versions/2.2.5
- https://rubygems.org/gems/carrierwave/versions/3.0.5
