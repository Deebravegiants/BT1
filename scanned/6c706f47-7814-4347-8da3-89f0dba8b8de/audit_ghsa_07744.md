# [H] opa-envoy-plugin has an Authorization Bypass via Double-Slash Path Misinterpretation in input.parsed_path

## Summary
Severity: High
Advisory: GHSA-9f29-v6mm-pw6w
CVE: CVE-2026-26205
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-9f29-v6mm-pw6w
Type: github-advisory

## Affected
- Go: `github.com/open-policy-agent/opa-envoy-plugin` — affected >=0 <1.13.2-envoy-2

## Details
A security vulnerability has been discovered in how the `input.parsed_path` field is constructed. HTTP request paths are treated as full URIs when parsed; interpreting leading path segments prefixed with double slashes (`//`) as [authority](https://datatracker.ietf.org/doc/html/rfc3986#section-3.2) components, and therefore dropping them from the parsed path. This creates a path interpretation mismatch between authorization policies and backend servers, enabling attackers to bypass access controls by crafting requests where the authorization filter evaluates a different path than the one ultimately served.

#### Attack example

**HTTP request:**

```
GET //admin/users HTTP/1.1
Host: example.com
```

**Policy sees:**

The leading `//admin` path segment is interpreted as an authority component, and dropped from `input.parsed_path` field:


```json
{
  "parsed_path": ["users"]
}
```

**Backend receives:**

`//admin/users` path, normalized to `/admin/users`.

#### Affected Request Pattern Examples

| Request path | `input.parsed_path` | `input.attributes.request.http.path` | Discrepancy |
| - | - | - | - |
| / | [""] | / | ✅ None |
| //foo  | [""] | //foo| ❌ Mismatch |
| /admin | ["admin"] | /admin | ✅ None |
| /admin/users | ["admin", "users"] |  /admin/users | ✅ None |
| //admin/users  | ["users"] | //admin/users | ❌ Mismatch |

### Impact

Users are impacted if all the following conditions apply:

1. Protected resources are path-hierarchical (e.g., `/admin/users` vs `/users`)
2. Authorization policies use `input.parsed_path` for path-based decisions
3. Backend servers apply lenient path normalization

### Patches

Go: `v1.13.2-envoy-2`
Docker: `1.13.2-envoy-2`, `1.13.2-envoy-2-static`

### Workarounds

Users who cannot immediately upgrade opa-envoy-plugin are recommended to apply one, or more, of the workarrounds described below.

#### 1. Enable the `merge_slashes` Envoy configuration option

As per [Envoy best practices](https://www.envoyproxy.io/docs/envoy/v1.37.0/configuration/best_practices/edge.html), enabling the [merge_slashes](https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/filters/network/http_connection_manager/v3/http_connection_manager.proto#envoy-v3-api-field-extensions-filters-network-http-connection-manager-v3-httpconnectionmanager-merge-slashes) configuration option in Envoy will remove redundant slashes from the request path before filtering is applied, effectively mitigating the `input.parsed_path` issue described in this advisory.


#### 2. Use `input.attributes.request.http.path` instead of `input.parsed_path` in policies

The `input.attributes.request.http.path` field contains the unprocessed, raw request path. Users are recommended to update any policy using `input.parsed_path` to instead use the `input.attributes.request.http.path` field.

##### Example ####

```rego
package example

# Use instead of input.parsed_path
parsed_path := split(                                        # tokenize into array
	trim_left(                                               # drop leading slashes
		urlquery.decode(input.attributes.request.http.path), # url-decode the path
		"/",
	),
	"/",
)
```

## References
- https://github.com/open-policy-agent/opa-envoy-plugin/security/advisories/GHSA-9f29-v6mm-pw6w
- https://nvd.nist.gov/vuln/detail/CVE-2026-26205
- https://github.com/open-policy-agent/opa-envoy-plugin/commit/58c44d4ec408d5852d1d0287599e7d5c5e2bc5c3
- https://github.com/open-policy-agent/opa-envoy-plugin
- https://github.com/open-policy-agent/opa-envoy-plugin/releases/tag/v1.13.2-envoy-2
