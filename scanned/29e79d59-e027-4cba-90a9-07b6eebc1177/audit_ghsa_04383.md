# [C] PhoenixStorybook: Unauthenticated remote code execution via HEEx template injection in phoenix_storybook playground

## Summary
Severity: Critical
Advisory: GHSA-55hg-8qxv-qj4p
CVE: CVE-2026-8467
CWE: CWE-94
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-55hg-8qxv-qj4p
Type: github-advisory

## Affected
- Hex: `phoenix_storybook` — affected >=0.5.0 <1.1.0

## Details
### Summary
An unsafe HEEx template generation vulnerability allows any unauthenticated user to execute arbitrary code on the server. The phoenix_storybook playground accepts user-controlled attribute values over WebSocket and interpolates them unsanitized into a HEEx template that is subsequently compiled and evaluated with full Elixir `Kernel` access.

### Details
The vulnerability is a three-step chain:

**1. Unsanitized WebSocket input (`extra_assigns_helpers.ex`)**
The `psb-assign` event handler in `PhoenixStorybook.Story.PlaygroundPreviewLive` accepts arbitrary attribute names and values from unauthenticated WebSocket clients and  stores them verbatim via `ExtraAssignsHelpers.handle_set_variation_assign/3`.

**2. Unescaped interpolation into HEEx (`component_renderer.ex`)**
`ComponentRenderer.attributes_markup/1` builds a HEEx template string by interpolating binary attribute values directly:
```elixir
{name, val} when is_binary(val) ->
  ~s|#{name}="#{val}"|
```
No escaping of `"` or `{` is performed. A value such as `foo" injected={EXPR} bar="` breaks out of the attribute string and injects `EXPR` as an inline HEEx expression.

**3. Unsandboxed evaluation (`component_renderer.ex`)**
The resulting HEEx string is compiled via `EEx.compile_string/2` and evaluated via `Code.eval_quoted_with_env/3` with full `Kernel` imports and no sandbox. The injected expression executes on the server even if it causes a rendering error.

### PoC
1. Identify any story URL with a Playground tab (e.g. `/storybook/core_components/button`).
2. Connect to the Phoenix LiveView WebSocket without any authentication.
3. Join the story's LiveView channel and send a `psb-assign` event with an attribute value that escapes the HEEx attribute context and embeds an Elixir expression (e.g. a `System.cmd/2` call).
4. The server evaluates the injected expression and returns its output in the rendered response.

No authentication, no special configuration, and no user interaction are required.

### Impact
This is a pre-authentication remote code execution vulnerability. Any user able to reach the storybook endpoint, including unauthenticated internet users if the storybook is publicly deployed, can execute arbitrary operating system commands with the privileges of the server process. All versions of `phoenix_storybook` from 0.5.0 before 1.1.0 are affected.

## Resources

* Introduction Commit: https://github.com/phenixdigital/phoenix_storybook/commit/e35379dfe2ef1a71b141899e36f431017c55265d
* Patch Commit: https://github.com/phenixdigital/phoenix_storybook/commit/56ab8464d4375fa52db806148a06cce126ad481d

## References
- https://github.com/phenixdigital/phoenix_storybook/security/advisories/GHSA-55hg-8qxv-qj4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-8467
- https://github.com/phenixdigital/phoenix_storybook/commit/56ab8464d4375fa52db806148a06cce126ad481d
- https://cna.erlef.org/cves/CVE-2026-8467.html
- https://github.com/phenixdigital/phoenix_storybook
- https://osv.dev/vulnerability/EEF-CVE-2026-8467
