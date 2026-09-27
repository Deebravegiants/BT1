# [H] Camaleon CMS vulnerable to arbitrary path traversal (GHSL-2024-183)

## Summary
Severity: High
Advisory: GHSA-cp65-5m9r-vc2c
CVE: CVE-2024-46987
CWE: CWE-200, CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-18
Source: https://github.com/advisories/GHSA-cp65-5m9r-vc2c
Type: github-advisory

## Affected
- RubyGems: `camaleon_cms` — affected >=0 <2.8.1

## Details
A path traversal vulnerability accessible via MediaController's download_private_file method allows authenticated users to download any file on the web server Camaleon CMS is running on (depending on the file permissions).

In the [download_private_file](https://github.com/owen2345/camaleon-cms/blob/feccb96e542319ed608acd3a16fa5d92f13ede67/app/controllers/camaleon_cms/admin/media_controller.rb#L28) method:
```ruby
def download_private_file
  cama_uploader.enable_private_mode!

  file = cama_uploader.fetch_file("private/#{params[:file]}")

  send_file file, disposition: 'inline'
end
```
The file parameter is passed to the [fetch_file](https://github.com/owen2345/camaleon-cms/blob/feccb96e542319ed608acd3a16fa5d92f13ede67/app/uploaders/camaleon_cms_local_uploader.rb#L27) method of the CamaleonCmsLocalUploader class (when files are uploaded locally):
```ruby
def fetch_file(file_name)
  raise ActionController::RoutingError, 'File not found' unless file_exists?(file_name)

  file_name
end
```
If the file exists it's passed back to the download_private_file method where the file is sent to the user via [send_file](https://github.com/owen2345/camaleon-cms/blob/feccb96e542319ed608acd3a16fa5d92f13ede67/app/controllers/camaleon_cms/admin/media_controller.rb#L33-L34).

Proof of concept
An authenticated user can download the /etc/passwd file by visiting an URL such as:

https://<camaleon-host>/admin/media/download_private_file?file=../../../../../../etc/passwd
Impact
This issue may lead to Information Disclosure.

Remediation
Normalize file paths constructed from untrusted user input before using them and check that the resulting path is inside the targeted directory. Additionally, do not allow character sequences such as .. in untrusted input that is used to build paths.

See also:

[CodeQL: Uncontrolled data used in path expression](https://codeql.github.com/codeql-query-help/ruby/rb-path-injection/)
[OWASP: Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)

## References
- https://github.com/owen2345/camaleon-cms/security/advisories/GHSA-cp65-5m9r-vc2c
- https://nvd.nist.gov/vuln/detail/CVE-2024-46987
- https://github.com/owen2345/camaleon-cms/commit/071b1b09d6d61ab02a5960b1ccafd9d9c2155a3e
- https://codeql.github.com/codeql-query-help/ruby/rb-path-injection
- https://github.com/owen2345/camaleon-cms
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/camaleon_cms/CVE-2024-46987.yml
- https://owasp.org/www-community/attacks/Path_Traversal
- https://securitylab.github.com/advisories/GHSL-2024-182_GHSL-2024-186_Camaleon_CMS
- https://www.reddit.com/r/rails/comments/1exwtdm/camaleon_cms_281_has_been_released
