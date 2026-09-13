# [H] GraphQL Modules has a Race Condition issue

## Summary
Severity: High
Advisory: GHSA-53wg-r69p-v3r7
CVE: CVE-2026-23735
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-53wg-r69p-v3r7
Type: github-advisory

## Affected
- npm: `graphql-modules` — affected >=2.2.1 <2.4.1
- npm: `graphql-modules` — affected >=3.0.0 <3.1.1

## Details
### Summary
Originally reported as an issue #2613 but should be elevated to a security issue as the ExecutionContext is often used to pass authentication tokens from incoming requests to services loading data from backend APIs.

### Details
When 2 or more parallel requests are made which trigger the same service, the context of the requests is mixed up in the service when the context is injected via `@ExecutionContext()`

### PoC

In a new project/folder, create and install the following `package.json`:

```json
{
  "name": "GHSA-53wg-r69p-v3r7",
  "scripts": {
    "test": "jest"
  },
  "dependencies": {
    "graphql-modules": "2.4.0"
  },
  "devDependencies": {
    "@babel/plugin-proposal-class-properties": "^7.18.6",
    "@babel/plugin-proposal-decorators": "^7.28.6",
    "babel-plugin-parameter-decorator": "^1.0.16",
    "jest": "^29.7.0",
    "reflect-metadata": "^0.2.2"
  }
}
```

with:

```
npm i
```

configure `babel.config.json` using:

```json
{
  "plugins": [
    ["@babel/plugin-proposal-decorators", { "legacy": true }],
    "babel-plugin-parameter-decorator",
    "@babel/plugin-proposal-class-properties"
  ]
}
```

then write the following test `GHSA-53wg-r69p-v3r7.spec.ts`:

```js
require("reflect-metadata");
const {
  createApplication,
  createModule,
  Injectable,
  Scope,
  ExecutionContext,
  gql,
  testkit,
} = require("graphql-modules");

test("accessing a singleton provider context during another asynchronous execution", async () => {
  @Injectable({ scope: Scope.Singleton })
  class IdentifierProvider {
    @ExecutionContext()
    context;

    getId() {
      return this.context.identifier;
    }
  }

  const { promise: gettingBefore, resolve: gotBefore } = createDeferred();

  const { promise: waitForGettingAfter, resolve: getAfter } = createDeferred();

  const mod = createModule({
    id: "mod",
    providers: [IdentifierProvider],
    typeDefs: gql`
      type Query {
        getAsyncIdentifiers: Identifiers!
      }

      type Identifiers {
        before: String!
        after: String!
      }
    `,
    resolvers: {
      Query: {
        async getAsyncIdentifiers(_0, _1, context) {
          const before = context.injector.get(IdentifierProvider).getId();
          gotBefore();
          await waitForGettingAfter;
          const after = context.injector.get(IdentifierProvider).getId();
          return { before, after };
        },
      },
    },
  });

  const app = createApplication({
    modules: [mod],
  });

  const document = gql`
    {
      getAsyncIdentifiers {
        before
        after
      }
    }
  `;

  const firstResult$ = testkit.execute(app, {
    contextValue: {
      identifier: "first",
    },
    document,
  });

  await gettingBefore;

  const secondResult$ = testkit.execute(app, {
    contextValue: {
      identifier: "second",
    },
    document,
  });

  getAfter();

  await expect(firstResult$).resolves.toEqual({
    data: {
      getAsyncIdentifiers: {
        before: "first",
        after: "first",
      },
    },
  });

  await expect(secondResult$).resolves.toEqual({
    data: {
      getAsyncIdentifiers: {
        before: "second",
        after: "second",
      },
    },
  });
});

function createDeferred() {
  let resolve, reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return {
    promise,
    resolve,
    reject,
  };
}
```

and execute using:

```
npm test
```

Your project tree should look like this:

```
GHSA-53wg-r69p-v3r7
    package.json
    package-lock.json
    babel.config.json
    GHSA-53wg-r69p-v3r7.spec.js
```

#### Expected vs. Actual Outcome

```diff
- Expected  - 1
+ Received  + 1

  Object {
    "data": Object {
      "getAsyncIdentifiers": Object {
-       "after": "first",
+       "after": "second",
        "before": "first",
      },
    },
  }
```

### Impact

Any application that uses services that inject the context using `@ExecutionContext()` from a singleton provider are at risk. The more traffic an application has, the higher the chance for parallel requests, the higher the risk.

## References
- https://github.com/graphql-hive/graphql-modules/security/advisories/GHSA-53wg-r69p-v3r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-23735
- https://github.com/graphql-hive/graphql-modules/issues/2613
- https://github.com/graphql-hive/graphql-modules/pull/2521
- https://github.com/graphql-hive/graphql-modules
- https://github.com/graphql-hive/graphql-modules/releases/tag/release-1768575025568
