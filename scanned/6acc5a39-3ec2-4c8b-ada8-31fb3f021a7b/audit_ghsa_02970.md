# [H] Cross-site Scripting Vulnerability in GraphQL Playground (distributed by Apollo Server)

## Summary
Severity: High
Advisory: GHSA-qm7x-rc44-rrqw
CWE: CWE-79
Ecosystem: npm
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-qm7x-rc44-rrqw
Type: github-advisory

## Affected
- npm: `apollo-server` — affected >=2.0.0 <2.25.3
- npm: `apollo-server` — affected >=3.0.0 <3.4.1

## Details
### Impact
In certain configurations, Apollo Server serves the client-side web app "GraphQL Playground" from the same web server that executes GraphQL operations. This web app has access to cookies and other credentials associated with the web server's operations. There is a cross-site scripting vulnerability in GraphQL Playground that allows for arbitrary JavaScript code execution in your web server's origin. If a user clicks a specially crafted link to your GraphQL Playground page served by Apollo Server, an attacker can steal cookies and other private browser data.

Details of the underlying GraphQL Playground vulnerability are available in [this `graphql-playground` advisory](https://github.com/graphql/graphql-playground/security/advisories/GHSA-59r9-6jp6-jcm7). (A [similar vulnerability](https://github.com/graphql/graphiql/security/advisories/GHSA-x4r7-m2q9-69c8) exists in the related `graphiql` project.) This advisory focuses on identifying whether *Apollo Server* installations are vulnerable and mitigating the vulnerability in Apollo Server; see the other advisories for details on the XSS vulnerability itself.

The impact of this vulnerability is more severe if (as is common) your GraphQL server's origin URL is an origin that is used to store sensitive data such as cookies.

In order for this vulnerability to affect your Apollo Server installation, it must actually serve GraphQL Playground. The integration between Apollo Server and GraphQL Playground is different in Apollo Server 2 and Apollo Server 3. You can tell which version of Apollo Server you are running by looking at the version of the [package from which you import the `ApolloServer` class](https://www.apollographql.com/docs/apollo-server/integrations/middleware/): this may be `apollo-server`, `apollo-server-express`, `apollo-server-lambda`, etc.

#### Apollo Server 3

Apollo Server 3 does not serve GraphQL Playground by default. It has a [landing page plugin system](https://www.apollographql.com/docs/apollo-server/api/plugin/landing-pages/) and the default plugin is a simple splash page that is not vulnerable to this exploit, linking to Apollo Sandbox Explorer. (We chose to change the default because GraphQL Playground is not actively maintained.)

If you are running Apollo Server 3, then you are *only* vulnerable if you *explicitly* import the [`ApolloServerPluginLandingPageGraphQLPlayground`](https://www.apollographql.com/docs/apollo-server/api/plugin/landing-pages/#graphql-playground-landing-page) plugin and pass it to your `ApolloServer`'s constructor in the `plugins` array. Otherwise, this advisory does not apply to your server.

#### Apollo Server 2

Apollo Server 2 serves GraphQL Playground by default, unless the `NODE_ENV` environment variable is set to `production`, or if you explicitly configure it via the `playground` option to the `ApolloServer` constructor.

Your Apollo Server 2 installation is vulnerable if *any* of the following is true:
- You pass `playground: true` to the `ApolloServer` constructor
- You pass some other object like `playground: {title: "Title"}` to the `ApolloServer` constructor
- You do *not* pass any `playground` option to the `ApolloServer` constructor, *and* the `NODE_ENV` environment variable is *not* set to `production`

#### Apollo Server 1

Apollo Server 1 included `graphiql` instead of `graphql-playground`. `graphiql` isn't automatically enabled in Apollo Server 1: you have to explicitly call a function such as `graphiqlExpress` to enable it. Because Apollo Server 1 is not commonly used, we have not done a detailed examination of whether the integration between Apollo Server 1 and `graphiql` is vulnerable to a similar exploit. If you are still using Apollo Server 1, we recommend you disable `graphiql` by removing the `graphiqlExpress` call, and then upgrade to a newer version of Apollo Server.

### Patches and workarounds

There are several approaches you can take to ensure that your server is not vulnerable to this issue.

#### Upgrade Apollo Server

The vulnerability has been patched in Apollo Server 2.25.3 and Apollo Server 3.4.1. To get the patch, upgrade your [Apollo Server entry point package](https://www.apollographql.com/docs/apollo-server/integrations/middleware/) to one of the fixed versions; this package may be `apollo-server`, `apollo-server-express`, `apollo-server-lambda`, etc. Additionally, if you depend directly on `apollo-server-core` in your `package.json`, make sure that you upgrade it to the same version.

#### Upgrade Playground version only

If upgrading to the latest version of Apollo Server 2 or 3 quickly will be challenging, you can configure your current version of Apollo Server to serve the latest version of the GraphQL Playground app. This will pin your app to serve a specific version of GraphQL Playground and you will not receive updates to it when you upgrade Apollo Server later, but this may be acceptable because GraphQL Playground is not actively maintained.

The way to do this depends on what version of Apollo Server you're using and if you're already configuring GraphQL Playground.

- **Apollo Server 3**: If you are using Apollo Server 3, then you are only vulnerable if your serve explicitly calls [`ApolloServerPluginLandingPageGraphQLPlayground`](https://www.apollographql.com/docs/apollo-server/api/plugin/landing-pages/#graphql-playground-landing-page) and passes it to the Apollo Server constructor in the `plugins` array. Add the option `version: '1.7.42'` to this call, so it looks like:
```
plugins: [ApolloServerPluginLandingPageGraphQLPlayground({version: '1.7.42'})]
```
- **Apollo Server 2 with no explicit `playground` option**: If you are using Apollo Server 2 and do not currently pass the `playground` option to `new ApolloServer`, add a `playground` option like so: 
```
new ApolloServer({ playground: process.env.NODE_ENV === 'production' ? false : { version: '1.7.42' } })
```
- **Apollo Server 2 with `playground: true` or `playground: {x, y, z}`**: If you are using Apollo Server 2 and currently pass `true` or an object to `new ApolloServer`, pass the `version` option under the `playground` option like so:
```
new ApolloServer({ playground: { version: '1.7.42', x, y, z } })
```

#### Disable GraphQL Playground

If upgrading Apollo Server or GraphQL Playground is challenging, you can also disable GraphQL Playground.

In Apollo Server 3, remove the call to `ApolloServerPluginLandingPageGraphQLPlayground` from your `ApolloServer` constructor's `plugins` array. This will replace GraphQL Playground with a simple splash page. See [the landing page plugins docs](https://www.apollographql.com/docs/apollo-server/api/plugin/landing-pages/) for details.

In Apollo Server 2, add `playground: false` to your `ApolloServer` constructor: `new ApolloServer({ playground: false })`. This will replace GraphQL Playground with an attempt to execute a GraphQL operation, which will likely display an error in the browser.

If you disable GraphQL Playground, any users who rely on it to execute GraphQL operations will need an alternative, such as the [Apollo Studio Explorer's account-free Sandbox](https://www.apollographql.com/docs/studio/explorer/#account-free-sandbox).

### Credit

This vulnerability was discovered by @Ry0taK. Thank you!

The fix to GraphQL Playground was developed by @acao and @glasser with help from @imolorhe, @divyenduz, and @benjie.


### For more information
If you have any questions or comments about this advisory:
* Read the [`graphql-playground` advisory](https://github.com/graphql/graphql-playground/security/advisories/GHSA-59r9-6jp6-jcm7)
* Open an issue in [the `apollo-server` repo](https://github.com/apollographql/apollo-server/)
* If the issue involves confidential information, email us at [security@apollographql.com](mailto:security@apollographql.com)

## References
- https://github.com/apollographql/apollo-server/security/advisories/GHSA-qm7x-rc44-rrqw
- https://github.com/apollographql/apollo-server
