# [C] Spin applications with specific configuration vulnerable to potential network sandbox escape

## Summary
Severity: Critical
Advisory: GHSA-f3h7-gpjj-wcvh
CVE: CVE-2024-32980
CWE: CWE-610
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-08
Source: https://github.com/advisories/GHSA-f3h7-gpjj-wcvh
Type: github-advisory

## Affected
- crates.io: `spin-sdk` — affected >=0 <2.4.3

## Details
### Impact
Some specifically configured Spin applications that use `self` requests without a specified URL authority can be induced to make requests to arbitrary hosts via the `Host` HTTP header.

If an application's manifest contains a component with configuration such as
```toml
allowed_outbound_hosts = ["http://self", "https://self"]
```

and code such as
```rust
 let res: Response = spin_sdk::http::send(
        Request::new(Method::Get, "/") // Note: the request URI does not contain a URL authority
 ).await?;
```

Then that application can be induced to send an outgoing request to another host (leading the app to process the response assuming it comes from another component in the same application). This can be induced with a request such as
```shell
curl -H"Host: google.com:80" localhost:3000 # Assuming the application is served on localhost:3000
```

> Note: If using a SDK that does not use `wasi:http/outgoing-handler`, the port can be omitted from the URL.

#### Vulnerable Configurations

The following conditions need to be met for an application to be vulnerable:
1. The environment Spin is deployed in routes requests to the Spin runtime based on the request URL instead of the `Host` header, and leaves the `Host` header set to the original value by the client.
2. The Spin application's component handling the incoming request is configured with an `allowed_outbound_hosts` list containing `"self"`.
3. In reaction to an incoming request, the component makes an outbound request whose URL doesn't include the hostname/port.

If all of these conditions apply, then Spin will use the inbound request's `Host` header to determine the `authority` part of the URL if none is explicitly provided in the request's URL.

#### Setups known not to be vulnerable

Fermyon's [Fermyon Cloud](https://developer.fermyon.com/cloud/index) serverless product and applications hosted on it are known not to be vulnerable.


### Patches
_Has the problem been patched? What versions should users upgrade to?_
Spin version 2.4.3 is being released with this advisory going public.

### Workarounds
For deployments of Spin, a workaround is to ensure that the `Host` header is sanitized to match the application a request is routed to.

For individual applications, multiple workarounds exist:
1. Ensure that outgoing requests always sanitize the `Host` header
2. Ensure that outgoing requests always provide the hostname in the URL and use that hostname in the `allowed_outbound_hosts` list instead of `self`
3. When using Spin 2.4, use [application-internal service chaining](https://developer.fermyon.com/spin/v2/http-outbound#local-service-chaining) for intra-application requests

## References
- https://github.com/fermyon/spin/security/advisories/GHSA-f3h7-gpjj-wcvh
- https://nvd.nist.gov/vuln/detail/CVE-2024-32980
- https://github.com/fermyon/spin/commit/b3db535c9edb72278d4db3a201f0ed214e561354
- https://github.com/fermyon/spin
