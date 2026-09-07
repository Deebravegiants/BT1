# [M] apollo-server-core vulnerable to URL-based XSS attack affecting IE11 on default landing page

## Summary
Severity: Medium
Advisory: GHSA-2fvv-qxrq-7jq6
CWE: CWE-79
Ecosystem: npm
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-2fvv-qxrq-7jq6
Type: github-advisory

## Affected
- npm: `apollo-server-core` — affected >=3.0.0 <3.10.1

## Details
### Impact

The default landing page contained HTML to display a sample `curl` command which is made visible if the full landing page bundle could not be fetched from Apollo's CDN. The server's URL is directly interpolated into this command inside the browser from `window.location.href`. On some older browsers such as IE11, this value is not URI-encoded. On such browsers, opening a malicious URL pointing at an Apollo Router could cause execution of attacker-controlled JavaScript.

This only affects Apollo Server with the [default landing page](https://www.apollographql.com/docs/apollo-server/api/plugin/landing-pages/) enabled. Old browsers visiting your server may be affected if ANY of these apply:
- You do not pass any landing page plugin to the `plugins` option of `new ApolloServer`.
- You pass `ApolloServerPluginLandingPageLocalDefault()` or `ApolloServerPluginLandingPageProductionDefault()` to the `plugins` option of `new ApolloServer`.

Browsers visiting your server are NOT affected if ANY of these apply:
- You pass `ApolloServerPluginLandingPageDisabled()` to the `plugins` option of `new ApolloServer`.
- You pass `ApolloServerPluginLandingPageGraphQLPlayground()` to the `plugins` option of `new ApolloServer`.
- You pass a custom plugin implementing the `renderLandingPage` hook to the `plugins` option of `new ApolloServer`.

This issue was introduced in v3.0.0 when the landing page feature was added.

### Patches
To avoid this, the sample `curl` command has been removed in release 3.10.1.

### Workarounds

Disabling the landing page removes the possibility of exploit:

```ts
import { ApolloServerPluginLandingPageDisabled } from 'apollo-server-core';

new ApolloServer({
  plugins: [ApolloServerPluginLandingPageDisabled()],
  // ...
});
```

### See also
A similar issue exists in the landing page of Apollo Router. See the corresponding [Apollo Router security advisory](https://github.com/apollographql/router/security/advisories/GHSA-p5q6-hhww-f999).

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Apollo Server repository](https://github.com/apollographql/apollo-server/)
* Email us at [security@apollographql.com](mailto:security@apollographql.com)

### Credits

This issue was discovered by Adrian Denkiewicz of [Doyensec](https://doyensec.com/research.html).

## References
- https://github.com/apollographql/apollo-server/security/advisories/GHSA-2fvv-qxrq-7jq6
- https://github.com/apollographql/apollo-server/commit/68a439b6e3af9edc8a2480092f2d49f058be1e64
- https://github.com/apollographql/apollo-server
