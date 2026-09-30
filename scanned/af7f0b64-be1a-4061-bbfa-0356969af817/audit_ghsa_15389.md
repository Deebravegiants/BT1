# [H] Apollo Router Coprocessors may cause Denial-of-Service when handling request bodies

## Summary
Severity: High
Advisory: GHSA-x6xq-whh3-gg32
CVE: CVE-2024-43783
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-x6xq-whh3-gg32
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=1.7.0 <1.52.1

## Details
## Impact

Instances of the Apollo Router using either of the following may be impacted by a denial-of-service vulnerability.

1. External Coprocessing with specific configurations; or
2. Native Rust Plugins accessing the Router request body in the RouterService layer 

Router customizations using Rhai scripts are **not** impacted.

### When using External Coprocessing:

Instances of the Apollo Router running versions >=1.21.0 and <1.52.1 are impacted by a denial-of-service vulnerability if **all** of the following are true:

1. Router has been configured to support External Coprocessing.
2. Router has been configured to send request bodies to coprocessors. This is a non-default configuration and must be configured intentionally by administrators.

You can identify if you are impacted by reviewing your router's configuration YAML for the following config:

```yaml
...
coprocessor:
  url: http://localhost:9000 # likely different in your environment
  router:
    request:
      body: true # this must be set to 'true' to be impacted
...
```
External Coprocessing was initially made available as an experimental feature with [Router version 1.21.0](https://github.com/apollographql/router/releases/tag/v1.21.0) on 2023-06-20 and was made generally available with [Router version 1.38.0](https://github.com/apollographql/router/releases/tag/v1.38.0) on 2024-01-19. More information about the Router’s [External Coprocessing feature is available here](https://www.apollographql.com/docs/router/customizations/coprocessor).

### When using Native Rust Plugins:

Instances of the Apollo Router running versions >=1.7.0 and <1.52.1 are impacted by a denial-of-service vulnerability if **all** of the following are true:

1. Router has been configured to use a custom-developed Native Rust Plugin
2. The plugin accesses `Request.router_request` in the `RouterService` layer
3. You are accumulating the body from `Request.router_request` into memory

To use a plugin, you need to be running a customized Router binary. Additionally, you need to have a `plugins` section with at least one plugin defined in your Router’s configuration YAML. That plugin would also need to define a custom `router_service` method.

You can check for a defined plugin by reviewing for the following in your Router’s configuration YAML:

```yaml
...
plugins:
    custom_plugin_name:
        # custom config here
...
```

You can check for a custom `router_service` method in a plugin, by reviewing for the following function signature in your plugin’s source:

```rust
fn router_service(&self, service: router::BoxService) -> router::BoxService
```

More information about the Router’s [Native Rust Plugin feature is available here](https://www.apollographql.com/docs/router/customizations/native).

## Impact Detail

If using an impacted configuration, the Router will load entire HTTP request bodies into memory without respect to other HTTP request size-limiting configurations like `limits.http_max_request_bytes`. This can cause the Router to be out-of-memory (OOM) terminated if a sufficiently large request is sent to the Router.

By default, the Router sets `limits.http_max_request_bytes` to 2 MB. More information about the Router’s [request limiting features is available here](https://www.apollographql.com/docs/router/configuration/overview/#request-limits).

## Patches

[Apollo Router 1.52.1](https://github.com/apollographql/router/releases/tag/v1.52.1)

If you have an impacted configuration as defined above, please upgrade to at least Apollo Router 1.52.1.

## Workarounds
If you cannot upgrade, you can mitigate the denial-of-service opportunity impacting External Coprocessors by setting the `coprocessor.router.request.body` configuration option to `false`. Please note that changing this configuration option will change the information sent to any coprocessors you have configured and may impact functionality implemented by those coprocessors. 

If you have developed a Native Rust Plugin and cannot upgrade, you can update your plugin to either not accumulate the request body or enforce a maximum body size limit. 

You can also mitigate this issue by limiting HTTP body payload sizes prior to the Router (e.g., in a proxy or web application firewall appliance).

## References
[Apollo Router 1.52.1 Release Notes](https://github.com/apollographql/router/releases/tag/v1.52.1)
[External Coprocessing documentation](https://www.apollographql.com/docs/router/customizations/coprocessor)
[HTTP Request Limiting documentation](https://www.apollographql.com/docs/router/configuration/overview/#request-limits)
[Native Rust Plugin documentation](https://www.apollographql.com/docs/router/customizations/native)

## References
- https://github.com/apollographql/router/security/advisories/GHSA-x6xq-whh3-gg32
- https://nvd.nist.gov/vuln/detail/CVE-2024-43783
- https://github.com/apollographql/router/commit/7a9c020608a62dcaa306b72ed0f6980f15923b14
- https://github.com/apollographql/router
- https://github.com/apollographql/router/releases/tag/v1.52.1
- https://www.apollographql.com/docs/router/configuration/overview/#request-limits
- https://www.apollographql.com/docs/router/customizations/coprocessor
- https://www.apollographql.com/docs/router/customizations/native
