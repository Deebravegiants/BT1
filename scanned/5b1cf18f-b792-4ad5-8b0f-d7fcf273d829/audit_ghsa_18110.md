# [H] Apollo Embedded Sandbox and Explorer vulnerable to CSRF via window.postMessage origin-validation bypass

## Summary
Severity: High
Advisory: GHSA-w87v-7w53-wwxv
CVE: CVE-2025-59845
CWE: CWE-346, CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2025-09-26
Source: https://github.com/advisories/GHSA-w87v-7w53-wwxv
Type: github-advisory

## Affected
- npm: `@apollo/sandbox` — affected >=0 <2.7.2
- npm: `@apollo/explorer` — affected >=0 <3.7.3

## Details
### Impact

A **Cross-Site Request Forgery (CSRF)** vulnerability was identified in Apollo’s **Embedded Sandbox** and **Embedded Explorer**.

The vulnerability arises from missing origin validation in the client-side code that handles `window.postMessage` events. A malicious website can send forged messages to the embedding page, causing the victim’s browser to execute arbitrary GraphQL queries or mutations against their GraphQL server while authenticated with the victim’s cookies.

#### Who is impacted

Anyone embedding [Apollo Sandbox](https://www.apollographql.com/docs/graphos/platform/sandbox#embedding-sandbox) or [Apollo Explorer](https://www.apollographql.com/docs/graphos/platform/explorer/embed) in their website may have been affected by this vulnerability.

- Users who embed Apollo Sandbox or Apollo Explorer in their websites via npm packages (`@apollo/sandbox` and `@apollo/explorer`) or direct links to Apollo’s CDN.
- Users running Apollo Router with [embedded Sandbox enabled](https://www.apollographql.com/docs/graphos/routing/configuration/yaml#sandbox). This served the vulnerable code from Apollo’s CDN.
- Users running Apollo Server with embedded Sandbox or Explorer enabled. Embedded Sandbox is enabled by default when `NODE_ENV` is not set to `production`, and embedded Sandbox and Explorer can also be enabled in production mode via [landing page plugins](https://www.apollographql.com/docs/apollo-server/api/plugin/landing-pages). This served the vulnerable code from Apollo’s CDN.

While all of the above methods of serving Embedded Sandbox and Explorer were vulnerable, Apollo has already updated its CDN to remove all vulnerable versions. **Unless you install the npm package `@apollo/sandbox` or `@apollo/explorer` directly into your website’s front end code, no action is necessary: the vulnerability has already been mitigated.**

Users who do not embed Sandbox/Explorer on their websites, or who only run Apollo Router/Server with production defaults were never impacted. The use of non-embedded Sandbox and Explorer hosted on [studio.apollographql.com](http://studio.apollographql.com/) is not vulnerable.


#### Scope of impact

The vulnerability allows a malicious website to open the vulnerable website in a new window and force it to send GraphQL requests to its origin. The requests themselves are not "cross-origin" as they are directly issued from the vulnerable website, but their contents are dictated by the malicious website.

The malicious website cannot read the responses to the GraphQL operations, but the operations may be mutations with side effects (such as using credentials to update app-specific data access controls). These operations can contain the browser user's cookies, and the vulnerable website may be on a private network otherwise inaccessible to the attacker. Operations sent this way look and exactly like legitimate operations sent by a human interacting with the embedded Sandbox or Explorer.

### Patches

The issue has been fixed by adding strict origin validation to DOM message handling.

- `@apollo/sandbox`: Patched in v2.7.2 and later
- `@apollo/explorer`: Patched in v3.7.3 and later
- Apollo’s CDN embeds have been updated to patched versions. This protects embeds based on `<script>` tags pointing to Apollo’s CDN, as well as the Apollo Router and Apollo Server features. No action is necessary to adopt the fix in this case.

If you manually edited the `<script>` tag provided by the Explorer or Sandbox UI to replace the version string `_latest`, `v2`, or `v3` with a specific git-style SHA, you may find that the Explorer or Sandbox UI does not currently load. To fix this, use a supported URL instead, as documented for [Sandbox](https://www.apollographql.com/docs/graphos/platform/sandbox#embedding-sandbox) or [Explorer](https://www.apollographql.com/docs/graphos/platform/explorer/embed). (The third-party Go GraphQL server [gqlgen](https://github.com/99designs/gqlgen) provides a function ApolloSandboxHandler which serves an unsupported URL and was broken by our mitigations; upgrading to [gqlgen v0.17.81](https://github.com/99designs/gqlgen/releases/tag/v0.17.81) will resolve this issue.)

### Workarounds

- If you are using Apollo Server, ensure `NODE_ENV=production` is set in production to avoid unintentionally serving embedded Sandbox.
- Customers not using embedded Sandbox/Explorer are not affected and do not need to take action.


### References

- [Apollo Server CSRF Documentation](https://www.apollographql.com/docs/apollo-server/security/cors#preventing-cross-site-request-forgery-csrf)
- [Apollo Router Sandbox Configuration](https://www.apollographql.com/docs/graphos/routing/configuration/yaml#sandbox)
- [Apollo Explorer Embed Documentation](https://www.apollographql.com/docs/graphos/platform/explorer/embed)

## References
- https://github.com/apollographql/embeddable-explorer/security/advisories/GHSA-w87v-7w53-wwxv
- https://nvd.nist.gov/vuln/detail/CVE-2025-59845
- https://github.com/apollographql/embeddable-explorer
