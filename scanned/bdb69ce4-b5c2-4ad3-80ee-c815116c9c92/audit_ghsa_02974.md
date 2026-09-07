# [H] GraphiQL introspection schema template injection attack

## Summary
Severity: High
Advisory: GHSA-x4r7-m2q9-69c8
CVE: CVE-2021-41248
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-x4r7-m2q9-69c8
Type: github-advisory

## Affected
- npm: `graphiql` — affected >=0.5.0 <1.4.7

## Details
- [1. Impact](#11-impact)
  - [2. Scope](#12-scope)
  - [3. Patches](#13-patches)
    - [3.1 CDN bundle implementations may be automatically patched](#131-cdn-bundle-implementations-may-be-automatically-patched)
  - [4. Workarounds for Older Versions](#14-workarounds-for-older-versions)
  - [5. How to Re-create the Exploit](#15-how-to-re-create-the-exploit)
  - [6. Credit](#16-credit)
  - [7. References](#17-references)
  - [8. For more information](#18-for-more-information)

This is a security advisory for an XSS vulnerability in `graphiql`.

A similar vulnerability affects `graphql-playground`, a fork of `graphiql`. There is a corresponding `graphql-playground` [advisory](https://github.com/graphql/graphql-playground/security/advisories/GHSA-59r9-6jp6-jcm7) and [Apollo Server advisory](https://github.com/apollographql/apollo-server/security/advisories/GHSA-qm7x-rc44-rrqw).

## 1. Impact

All versions of `graphiql` older than [`graphiql@1.4.7`](https://github.com/graphql/graphiql/releases/tag/v1.4.7) are vulnerable to compromised HTTP schema introspection responses or `schema` prop values with malicious GraphQL type names, exposing a dynamic XSS attack surface that can allow code injection on operation autocomplete.

In order for the attack to take place, the user must load a vulnerable schema in `graphiql`. There are a number of ways that can occur.

By default, the schema URL is _not_ attacker-controllable in `graphiql` or in its suggested implementations or examples, leaving only very complex attack vectors.

If a custom implementation of `graphiql`'s `fetcher` allows the schema URL to be set dynamically, such as a URL query parameter like `?endpoint=` in `graphql-playground`, or a database provided value, then this custom `graphiql` implementation is _vulnerable to phishing attacks_, and thus much more readily available, low or no privelege level xss attacks. The URLs could look like any generic looking graphql schema URL.

Because this exposes an XSS attack surface, it would be possible for a threat actor to exfiltrate user credentials, data, etc. using arbitrary malicious scripts, without it being known to the user.

## 2. Scope

This advisory describes the impact on the `graphiql` package. The vulnerability also affects other projects forked from `graphiql` such as [`graphql-playground`](https://github.com/graphql/graphql-playground/security/advisories/GHSA-59r9-6jp6-jcm7) and the `graphql-playground` fork distributed by Apollo Server. The impact is more severe in the `graphql-playground` implementations; see the [`graphql-playground` advisory](https://github.com/graphql/graphql-playground/security/advisories/GHSA-59r9-6jp6-jcm7) and [Apollo Server advisory](https://github.com/apollographql/apollo-server/security/advisories/GHSA-qm7x-rc44-rrqw) for details.

This vulnerability does not impact `codemirror-graphql`, `monaco-graphql` or other dependents, as it exists in `onHasCompletion.ts` in `graphiql`. It does impact all forks of `graphiql`, and every released version of `graphiql`.

It should be noted that desktop clients such as Altair, Insomnia, Postwoman, do not appear to be impacted by this.

## 3. Patches

`graphiql@1.4.7` addresses this issue via defense in depth.

- **HTML-escaping text** that should be treated as text rather than HTML. In most of the app, this happens automatically because React escapes all interpolated text by default. However, one vulnerable component uses the unsafe `innerHTML` API and interpolated type names directly into HTML. We now properly escape that type name, which fixes the known vulnerability.

- **Validates the schema** upon receiving the introspection response or schema changes. Schemas with names that violate the GraphQL spec will no longer be loaded. (This includes preventing the Doc Explorer from loading.) This change is also sufficient to fix the known vulnerability. You can disable this validation by setting `dangerouslyAssumeSchemaIsValid={true}`, which means you are relying only on escaping values to protect you from this attack.

- **Ensuring that user-generated HTML is safe**. Schemas can contain Markdown in `description` and `deprecationReason` fields, and the web app renders them to HTML using the `markdown-it` library. As part of the development of `graphiql@1.4.7`, we verified that our use of `markdown-it` prevents the inclusion of arbitrary HTML. We use `markdown-it` without setting `html: true`, so we are comfortable relying on [`markdown-it`'s HTML escaping](https://github.com/markdown-it/markdown-it/blob/master/docs/security.md) here. We considered running a second level of sanitization over all rendered Markdown using a library such as `dompurify` but believe that is unnecessary as `markdown-it`'s sanitization appears to be adequate. `graphiql@1.4.7` does update to the latest version of `markdown-it` (v12, from v10) so that any security fixes in v11 and v12 will take effect.

### 3.1 CDN bundle implementations may be automatically patched

Note that if your implementation is depending on a CDN version of `graphiql`, and is pointed to the `latest` tag (usually the default for most cdns if no version is specified) then this issue is already mitigated, in case you were vulnerable to it before.

## 4. Workarounds for Older Versions

If you cannot use `graphiql@1.4.7` or later

- Always use a static URL to a trusted server that is serving a trusted GraphQL schema.

- If you have a custom implementation that allows using user-provided schema URLs via a query parameter, database value, etc, you must either disable this customization, or only allow trusted URLs.

## 5. How to Re-create the Exploit

You can see an example on [codesandbox](https://codesandbox.io/s/graphiql-xss-exploit-gr22f?file=/src/App.js). These are both fixed to the last `graphiql` release `1.4.6` which is the last vulnerable release; however it would work with any previous release of `graphiql`.

Both of these examples are meant to demonstrate the phishing attack surface, so they are customized to accept a `url` parameter. To demonstrate the phishing attack, add `?url=https://graphql-xss-schema.netlify.app/graphql` to the in-codesandbox browser.

Erase the contents of the given query and type `{u`. You will see an alert window open, showing that attacker-controlled code was executed.

Note that when React is in development mode, a validation exception is thrown visibly; however that exception is usually buried in the browser console in a production build of `graphiql`. This validation exception comes from `getDiagnostics`, which invokes `graphql` `validate()` which in turn will `assertValidSchema()`, as `apollo-server-core` does on executing each operation. This validation does not prevent the exploit from being successful.

Note that something like the `url` parameter is not required for the attack to happen if `graphiql`'s `fetcher` is configured in a different way to communicate with a compromised GraphQL server.

## 6. Credit

This vulnerability was discovered by [@Ry0taK](https://github.com/Ry0taK), thank you! :1st_place_medal:

Others who contributed:

- [@imolorhe](https://github.com/imolorhe)
- [@glasser](https://github.com/glasser)
- [@divyenduz](https://github.com/divyenduz)
- [@dotansimha](https://github.com/dotansimha)
- [@acao](https://github.com/acao)
- [@benjie](https://github.com/benjie) and many others who provided morale support

## 7. References

**The vulnerability has always been present**

[In the first commit](https://github.com/graphql/graphiql/commit/b9dec272d89d9c590727fd10d62e4a47e0317fc7#diff-855b77f6310b7e4fb1bcac779cd945092ed49fd759f4684ea391b45101166437R87)

[And later moved to onHasCompletion.js in 2016](https://github.com/graphql/graphiql/commit/6701b0b626e43800e32413590a295e5c1e3d5419#diff-d45eb76aebcffd27d3a123214487116fa95e0b5a11d70a94a0ce3033ce09f879R110) (now `.ts` after the typescript migration)

## 8. For more information

If you have any questions or comments about this advisory:

- Open an issue in [graphiql repo](https://github.com/graphql/graphiql/new/issues)
- Read [more details](https://github.com/graphql/graphiql/blob/main/docs/security/2021-introspection-schema-xss.md#2-more-details-on-the-vulnerability) on the vulnerability

## References
- https://github.com/graphql/graphiql/security/advisories/GHSA-x4r7-m2q9-69c8
- https://github.com/graphql/graphql-playground/security/advisories/GHSA-59r9-6jp6-jcm7
- https://nvd.nist.gov/vuln/detail/CVE-2021-41248
- https://github.com/graphql/graphiql/commit/6701b0b626e43800e32413590a295e5c1e3d5419#diff-d45eb76aebcffd27d3a123214487116fa95e0b5a11d70a94a0ce3033ce09f879R110
- https://github.com/graphql/graphiql/commit/b9dec272d89d9c590727fd10d62e4a47e0317fc7#diff-855b77f6310b7e4fb1bcac779cd945092ed49fd759f4684ea391b45101166437R87
- https://github.com/graphql/graphiql/commit/cb237eeeaf7333c4954c752122261db7520f7bf4
- https://github.com/graphql/graphiql
- https://github.com/graphql/graphiql/blob/main/docs/security/2021-introspection-schema-xss.md#2-more-details-on-the-vulnerability
