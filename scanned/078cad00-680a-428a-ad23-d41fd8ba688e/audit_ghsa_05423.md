# [H] @envelop/graphql-modules has a Race Condition vulnerability

## Summary
Severity: High
Advisory: GHSA-h3hw-29fv-2x75
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-h3hw-29fv-2x75
Type: github-advisory

## Affected
- npm: `@envelop/graphql-modules` — affected >=0 <9.1.0

## Details
### Summary
Context race condition when using `useGraphQLModules` plugin

### Details

Related to: https://github.com/graphql-hive/graphql-modules/security/advisories/GHSA-53wg-r69p-v3r7

When 2 or more parallel requests are made which trigger the same service, the context of the requests is mixed up in the service when the context is injected via @ExecutionContext() and graphql-modules are used in Yoga with `useGraphQLModules(application)`. This issue was fixed in `graphql-modules` in `2.4.1` and `3.1.1` but using `useGraphQLModules` will bypass the `async_hooks` fix that was implemented.

### PoC

Create the following `package.json` and run `npm i`

```json
{
  "name": "poc",
  "scripts": {
    "compile": "tsc",
    "start": "npm run compile && node ./dist/src/index.js",
    "test": "npm run compile && node ./dist/test/bleedtest.js"
  },
  "dependencies": {
    "@envelop/graphql-modules": "^9.0.0",
    "graphql-yoga": "^5.0.0",
    "graphql": "^16.10.0",
    "graphql-modules": "3.1.1",
    "reflect-metadata": "0.2.1",
    "axios": "^1.8.4"
  },
  "devDependencies": {
    "@types/node": "^22.14.1",
    "typescript": "^5.8.3"
  }
}
```

Define the app entrypoint: `src/index.ts`

```ts
import { module } from "./module.js";
import { useGraphQLModules } from '@envelop/graphql-modules'
import { createApplication } from "graphql-modules";
import { createServer } from 'node:http'
import { randomUUID } from "node:crypto";
import { createYoga } from 'graphql-yoga';

const application = createApplication({
    modules: [module]
})

const yoga = createYoga({
    schema: application.schema,
    plugins: [useGraphQLModules(application)],
    context() {
        return {
            requestId: randomUUID(),
        }
    }
})

const server = createServer(yoga)
server.listen(4001, '127.0.0.1', undefined, () => {
    console.info(
        `[Server] Running on http://localhost:4001/graphql`
    )
})
```

Create the test module: `src/module.ts`

```ts
import { createModule, gql } from "graphql-modules";
import Service from "./service.js";

const typeDefs = gql`
    type Book {
        id1: String
        id2: String
    }
    type Query {
        books: [Book]
    }
`;

export const module = createModule({
    id: 'book-module',
    typeDefs: [typeDefs],
    providers: [Service],
    resolvers: {
        Query: {
            // return one empty book
            books: () => [{}],
        },
        Book: {
            // return the requestId from the context
            id1: async (_root, _args, { injector } ) => {
                return injector.get(Service).get();
            },
            // return the requestId from the context of the service 100 ms later
            id2: async (_root, _args, { injector } ) => {
                await new Promise(resolve => setTimeout(resolve, 100));
                return injector.get(Service).get()
            },
        }
    }
})
```

Add the Service that's to be injected `src/service.ts`

```ts
import { ExecutionContext, Injectable } from 'graphql-modules';
import 'reflect-metadata';

@Injectable()
export default class Service {
    @ExecutionContext()
    private context: ExecutionContext;

    get() {
        return this.context.requestId;
    }
}
```

Add the test case `test/bleedtest.js`

```ts
import axios from 'axios';

const url = 'http://localhost:4001/graphql';
const query = `query { books { id1 id2 } }`;

const makeGraphQLRequest = async () => {
    const response = await axios.post(url, { query });

    const book = response.data.data.books[0]
    if (book.id1 !== book.id2) {
        throw new Error(`wrong response with ids ${(book.id1)} and ${(book.id2)}`)
    }
}

const numberOfRequests = 2;
await Promise.all(Array.from(
    { length: numberOfRequests },
    makeGraphQLRequest,
));
```

Then run the server with `npm run start` in one terminal and the testcase in another with `npm run test`.
The returned IDs should be identical as they are both read from the context within the same request.
However, there is a mismatch:

```
❯ npm run test

> poc@1.0.0 test
> npm run compile && node ./dist/test/bleedtest.js


> poc@1.0.0 compile
> tsc

file://<redacted>/dist/test/bleedtest.js:8
        throw new Error(`wrong response with ids ${(book.id1)} and ${(book.id2)}`);
              ^

Error: wrong response with ids c2d83151-0922-4f25-a3e9-2f03acc1376a and e16c7335-0eaa-4386-b415-869ee4b05315
    at makeGraphQLRequest (file://<redacted>/dist/test/bleedtest.js:8:15)
    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)
    at async Promise.all (index 0)
    at async file://<redacted>/dist/test/bleedtest.js:12:1
```

### Impact
Any application that uses `useGraphQLModules` from `@envelop/graphql-modules` along with services that inject the context using @ExecutionContext() from a singleton provider are at risk. The more traffic an application has, the higher the chance for parallel requests, the higher the risk.

## References
- https://github.com/graphql-hive/envelop/security/advisories/GHSA-h3hw-29fv-2x75
- https://github.com/graphql-hive/graphql-modules/security/advisories/GHSA-53wg-r69p-v3r7
- https://github.com/graphql-hive/envelop/commit/ab49fa259a51d976c437e084114e070b99720ba9
- https://github.com/graphql-hive/envelop
- https://github.com/graphql-hive/envelop/releases/tag/release-1768928934700
