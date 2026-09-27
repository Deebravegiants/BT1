# [M] Rack's greedy multipart boundary parsing can cause parser differentials and WAF bypass.

## Summary
Severity: Medium
Advisory: GHSA-vgpv-f759-9wx3
CVE: CVE-2026-26961
CWE: CWE-436
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-vgpv-f759-9wx3
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.23
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.21
- RubyGems: `rack` — affected >=3.2.0 <3.2.6

## Details
## Summary

`Rack::Multipart::Parser` extracts the `boundary` parameter from `multipart/form-data` using a greedy regular expression. When a `Content-Type` header contains multiple `boundary` parameters, Rack selects the last one rather than the first.

In deployments where an upstream proxy, WAF, or intermediary interprets the first `boundary` parameter, this mismatch can allow an attacker to smuggle multipart content past upstream inspection and have Rack parse a different body structure than the intermediary validated.

## Details

Rack identifies the multipart boundary using logic equivalent to:

```ruby
MULTIPART = %r|\Amultipart/.*boundary=\"?([^\";,]+)\"?|ni
```

Because the expression is greedy, it matches the last `boundary=` parameter in a header such as:

```http
Content-Type: multipart/form-data; boundary=safe; boundary=malicious
```

As a result, Rack parses the request body using `malicious`, while another component may interpret the same header using `safe`.

This creates an interpretation conflict. If an upstream WAF or proxy inspects multipart parts using the first boundary and Rack later parses the body using the last boundary, a client may be able to place malicious form fields or uploaded content in parts that Rack accepts but the upstream component did not inspect as intended.

This issue is most relevant in layered deployments where security decisions are made before the request reaches Rack.

## Impact

Applications that accept `multipart/form-data` uploads behind an inspecting proxy or WAF may be affected.

In such deployments, an attacker may be able to bypass upstream filtering of uploaded files or form fields by sending a request with multiple `boundary` parameters and relying on the intermediary and Rack to parse the request differently.

The practical impact depends on deployment architecture. If no upstream component relies on a different multipart interpretation, this behavior may not provide meaningful additional attacker capability.

## Mitigation

* Update to a patched version of Rack that rejects ambiguous multipart `Content-Type` headers or parses duplicate `boundary` parameters consistently.
* Reject requests containing multiple `boundary` parameters.
* Normalize or regenerate multipart metadata at the trusted edge before forwarding requests to Rack.
* Avoid relying on upstream inspection of malformed multipart requests unless duplicate parameter handling is explicitly consistent across components.

## References
- https://github.com/rack/rack/security/advisories/GHSA-vgpv-f759-9wx3
- https://nvd.nist.gov/vuln/detail/CVE-2026-26961
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-26961.yml
