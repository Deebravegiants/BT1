# [H] Remote code execution in dependabot-core branch names when cloning

## Summary
Severity: High
Advisory: GHSA-23f7-99jx-m54r
CVE: CVE-2020-26222
CWE: CWE-74
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-11-13
Source: https://github.com/advisories/GHSA-23f7-99jx-m54r
Type: github-advisory

## Affected
- RubyGems: `dependabot-omnibus` — affected >=0.119.0.beta1 <0.125.1
- RubyGems: `dependabot-common` — affected >=0.119.0.beta1 <0.125.1

## Details
### Impact
Remote code execution vulnerability in `dependabot-common` and  `dependabot-go_modules` when a source branch name contains malicious injectable bash code.

For example, if Dependabot is configured to use the following source branch name: `"/$({curl,127.0.0.1})"`, Dependabot will make a HTTP request to the following URL: 127.0.0.1 when cloning the source repository.

When Dependabot is configured to clone the source repository during an update, Dependabot runs a shell command to git clone the repository:

```bash
git clone --no-tags --no-recurse-submodules --depth=1 --branch=<BRANCH> --single-branch <GITHUB_REPO_URL> repo/contents/path
```

Dependabot will always clone the source repository for `go_modules` during the file fetching step and can be configured to clone the repository for other package managers using the `FileFetcher` class from `dependabot-common`.

```ruby
source = Dependabot::Source.new(
  provider: "github",
  repo: "repo/name",
  directory: "/",
  branch: "/$({curl,127.0.0.1})",
)

repo_contents_path = "./file/path"
fetcher = Dependabot::FileFetchers.for_package_manager("bundler").
                  new(source: source, credentials: [],
                  repo_contents_path: repo_contents_path)
fetcher.clone_repo_contents
```

### Patches

The fix was applied to version `0.125.1`: https://github.com/dependabot/dependabot-core/pull/2727

### Workarounds
Escape the branch name prior to passing it to the `Dependabot::Source` class.

For example using `shellwords`:

```ruby
require "shellwords"
branch = Shellwords.escape("/$({curl,127.0.0.1})")
source = Dependabot::Source.new(
  provider: "github",
  repo: "repo/name",
  directory: "/",
  branch: branch,
)
```

## References
- https://github.com/dependabot/dependabot-core/security/advisories/GHSA-23f7-99jx-m54r
- https://nvd.nist.gov/vuln/detail/CVE-2020-26222
- https://github.com/dependabot/dependabot-core/pull/2727
- https://github.com/dependabot/dependabot-core/commit/e089116abbe284425b976f7920e502b8e83a61b5
- https://github.com/dependabot/dependabot-core
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/dependabot-common/CVE-2020-26222.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/dependabot-omnibus/CVE-2020-26222.yml
- https://rubygems.org/gems/dependabot-common
- https://rubygems.org/gems/dependabot-omnibus
