# [H] SQL Injection Vulnerability via ActiveRecord comments

## Summary
Severity: High
Advisory: GHSA-hq7p-j377-6v63
CVE: CVE-2023-22794
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-hq7p-j377-6v63
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=6.0.0 <6.0.6.1
- RubyGems: `activerecord` — affected >=6.1.0 <6.1.7.1
- RubyGems: `activerecord` — affected >=7.0.0 <7.0.4.1

## Details
There is a possible vulnerability in ActiveRecord related to the sanitization of comments. This vulnerability has been assigned the CVE identifier CVE-2023-22794.

Versions Affected: >= 6.0.0 Not affected: < 6.0.0 Fixed Versions: 6.0.6.1, 6.1.7.1, 7.0.4.1
Impact

Previously the implementation of escaping for comments was insufficient for

If malicious user input is passed to either the annotate query method, the optimizer_hints query method, or through the QueryLogs interface which automatically adds annotations, it may be sent to the database with insufficient sanitization and be able to inject SQL outside of the comment.

In most cases these interfaces won’t be used with user input and users should avoid doing so.

Example vulnerable code:
```
Post.where(id: 1).annotate("#{params[:user_input]}")

Post.where(id: 1).optimizer_hints("#{params[:user_input]}")
```
Example vulnerable QueryLogs configuration (the default configuration is not vulnerable):
```
config.active_record.query_log_tags = [
  {
    something: -> { <some value including user input> }
  }
]
```
All users running an affected release should either upgrade or use one of the workarounds immediately.
Releases

The FIXED releases are available at the normal locations.
Workarounds

Avoid passing user input to annotate and avoid using QueryLogs configuration which can include user input.
Patches

To aid users who aren’t able to upgrade immediately we have provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

    6-0-Make-sanitize_as_sql_comment-more-strict.patch - Patch for 6.0 series
    6-1-Make-sanitize_as_sql_comment-more-strict.patch - Patch for 6.1 series
    7-0-Make-sanitize_as_sql_comment-more-strict.patch - Patch for 7.0 series

Please note that only the 7.0.Z and 6.1.Z series are supported at present, and 6.0.Z for severe vulnerabilities. Users of earlier unsupported releases are advised to upgrade as soon as possible as we cannot guarantee the continued availability of security fixes for unsupported releases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22794
- https://github.com/rails/rails/commit/d7aba06953f9fa789c411676b941d20df8ef73de
- https://discuss.rubyonrails.org/t/cve-2023-22794-sql-injection-vulnerability-via-activerecord-comments/82117
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.0.4.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2023-22794.yml
- https://security.netapp.com/advisory/ntap-20240202-0008
- https://www.debian.org/security/2023/dsa-5372
