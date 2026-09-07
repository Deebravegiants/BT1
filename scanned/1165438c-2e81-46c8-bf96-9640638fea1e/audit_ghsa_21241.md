# [M] The graphql-upload library included in Apollo Server 2 is vulnerable to CSRF mutations

## Summary
Severity: Medium
Advisory: GHSA-2p3c-p3qw-69r4
CWE: CWE-352
Ecosystem: npm
Published: 2022-10-12
Source: https://github.com/advisories/GHSA-2p3c-p3qw-69r4
Type: github-advisory

## Affected
- npm: `apollo-server` — affected >=2.0.0 <2.25.4

## Details
### Impact
The [graphql-upload](https://www.npmjs.com/package/graphql-upload) npm package can execute GraphQL operations contained in `content-type: multipart/form-data` POST requests. Because they are POST requests, they can contain GraphQL mutations. Because they use `content-type: multipart/form-data`, they can be "simple requests" which are not preflighted by browsers.

If your GraphQL server uses `graphql-upload` and uses `SameSite=None` cookies for authentication, then JS on any origin can cause browsers to send cookie-authenticated mutations to your GraphQL server, which will be executed without checking your CORS policy first. (The attack won't be able to see the response to the mutation if your CORS policy is set up properly, but the side effects of the mutation will still happen.)

Additionally, if your GraphQL server uses `graphql-upload` and relies on network properties for security (whether by explicitly looking at the client's IP address or by only being available on a private network), then JS on any origin can cause browsers (which may be on a private network or have an allowed IP address) to send mutations to your GraphQL server, which will be executed without checking your CORS policy first. (This attack does not require your server to use cookies. It is in some cases prevented by some browsers such as Chrome.)

Apollo Server 2 bundled `graphql-upload` and enabled it by default, so by default, Apollo Server 2 servers are vulnerable to these CSRF attacks.  (Apollo Server 1 did not bundle `graphql-upload`. Apollo Server 3 no longer bundles `graphql-upload`, although AS3's docs do document how to manually integrate with `graphql-upload`.) It is enabled even if your server makes no use of the upload functionality.

If you are running Apollo Server 2 (older than v2.25.4) and do not specify `uploads: false` to `new ApolloServer`, then you are vulnerable to this CSRF mutation attack.

We recently introduced an opt-in CSRF prevention feature in Apollo Server 3.7.  This feature successfully protects against CSRF even if you have manually integrated your AS3.7 server with `graphql-upload`. However, this feature is not available for Apollo Server 2.

### Patches
If you are using Apollo Server 2 and do *not* actually use uploads in your schema (ie, the `Upload` scalar is not used as the argument to any field or in any input object definition, and you do not specify `uploads` to `new ApolloServer`), then upgrading to Apollo Server 2.25.4 will automatically disable `graphql-upload` in your server.  This will fix the CSRF mutation vulnerability.

Upgrading to v2.25.4 does still leave your server vulnerable to non-mutation CSRF attacks such as timing attacks against query operations. To protect yourself against these potentially lower impact CSRF attack, we encourage upgrading to Apollo Server v3.7 and enabling CSRF prevention. See [the Apollo Server 3 migration guide](https://www.apollographql.com/docs/apollo-server/migration/) and the [CSRF prevention docs](https://www.apollographql.com/docs/apollo-server/security/cors/#preventing-cross-site-request-forgery-csrf) for details.

If you are actively using the uploads feature with Apollo Server 2, then upgrading to v2.25.4 will not disable the feature and you will still be vulnerable. You should instead upgrade to v3.7 and enable the CSRF prevention feature.

If you are manually integrating the `graphql-upload` package with any version of Apollo Server (or any Node GraphQL server) and need to continue using the feature, then you must enable some sort of CSRF prevention feature to fix this vulnerability. We recommend the CSRF prevention feature in Apollo Server 3.7.

### Workarounds
Instead of upgrading your Apollo Server 2 server, you can specify `uploads: false` to `new ApolloServer` to disable the `graphql-upload` integration and protect against CSRF mutations. (Only do this if you do not actually use the uploads feature in your server!) This will still leave your server vulnerable to non-mutation CSRF attacks such as timing attacks against query operations; you need to upgrade to v3.7 and enable CSRF prevention to protect against these attacks.

### Related work
- [PR adding a Security section to the GraphQL multipart request spec](https://github.com/jaydenseric/graphql-multipart-request-spec/pull/64)

## References
- https://github.com/apollographql/apollo-server/security/advisories/GHSA-2p3c-p3qw-69r4
- https://github.com/jaydenseric/graphql-multipart-request-spec/pull/64
- https://github.com/apollographql/apollo-server/commit/82d44985ddca8e61557957d67f41e9c1a705a5ca
- https://github.com/apollographql/apollo-server
