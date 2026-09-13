# [H] Effect `AsyncLocalStorage` context lost/contaminated inside Effect fibers under concurrent load with RPC

## Summary
Severity: High
Advisory: GHSA-38f7-945m-qr2g
CVE: CVE-2026-32887
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-38f7-945m-qr2g
Type: github-advisory

## Affected
- npm: `effect` — affected >=0 <3.20.0

## Details
## Versions

- `effect`: 3.19.15
- `@effect/rpc`: 0.72.1
- `@effect/platform`: 0.94.2
- Node.js: v22.20.0
- Vercel runtime with Fluid compute
- Next.js: 16 (App Router)
- `@clerk/nextjs`: 6.x

## Root cause

Effect's `MixedScheduler` batches fiber continuations and drains them inside a **single** microtask or timer callback. The `AsyncLocalStorage` context active during that callback belongs to whichever request first triggered the scheduler's drain cycle — **not** the request that owns the fiber being resumed.

### Detailed mechanism

#### 1. Scheduler batching (`effect/src/Scheduler.ts`, `MixedScheduler`)

```typescript
// MixedScheduler.starve() — called once when first task is scheduled
private starve(depth = 0) {
  if (depth >= this.maxNextTickBeforeTimer) {
    setTimeout(() => this.starveInternal(0), 0)       // timer queue
  } else {
    Promise.resolve(void 0).then(() => this.starveInternal(depth + 1)) // microtask queue
  }
}

// MixedScheduler.starveInternal() — drains ALL accumulated tasks in one call
private starveInternal(depth: number) {
  const tasks = this.tasks.buckets
  this.tasks.buckets = []
  for (const [_, toRun] of tasks) {
    for (let i = 0; i < toRun.length; i++) {
      toRun[i]()  // ← Every fiber continuation runs in the SAME ALS context
    }
  }
  // ...
}
```

`scheduleTask` only calls `starve()` when `running` is `false`. Subsequent tasks accumulate in `this.tasks` until `starveInternal` drains them all. The `Promise.then()` (or `setTimeout`) callback inherits the ALS context from whichever call site created it — i.e., whichever request's fiber first set `running = true`.

**Result:** Under concurrent load, fiber continuations from Request A and Request B execute inside the same `starveInternal` call, sharing a single ALS context. If Request A triggered `starve()`, then Request B's fiber reads Request A's ALS context.

#### 2. `toWebHandlerRuntime` does not propagate ALS (`@effect/platform/src/HttpApp.ts:211-240`)

```typescript
export const toWebHandlerRuntime = <R>(runtime: Runtime.Runtime<R>) => {
  const httpRuntime: Types.Mutable<Runtime.Runtime<R>> = Runtime.make(runtime)
  const run = Runtime.runFork(httpRuntime)
  return <E>(self: Default<E, R | Scope.Scope>, middleware?) => {
    return (request: Request, context?): Promise<Response> =>
      new Promise((resolve) => {
        // Per-request Effect context is correctly set via contextMap:
        const contextMap = new Map<string, any>(runtime.context.unsafeMap)
        const httpServerRequest = ServerRequest.fromWeb(request)
        contextMap.set(ServerRequest.HttpServerRequest.key, httpServerRequest)
        httpRuntime.context = Context.unsafeMake(contextMap)

        // But the fiber is forked without any ALS propagation:
        const fiber = run(httpApp as any)  // ← ALS context is NOT captured or restored
      })
  }
}
```

Effect's own `Context` (containing `HttpServerRequest`) is correctly set per-request. But the **Node.js ALS context** — which frameworks like Next.js, Clerk, and OpenTelemetry rely on — is not captured at fork time or restored when the fiber's continuations execute.

#### 3. The dangerous pattern this enables

```typescript
// RPC handler — runs inside an Effect fiber
const handler = Effect.gen(function*() {
  // This calls auth() from @clerk/nextjs/server, which reads from ALS
  const { userId } = yield* Effect.tryPromise({
    try: async () => auth(),  // ← may read WRONG user's session
    catch: () => new UnauthorizedError({ message: "Auth failed" })
  })
  return yield* repository.getUser(userId)
})
```

The `async () => auth()` thunk executes when the fiber continuation is scheduled by `MixedScheduler`. At that point, the ALS context belongs to an arbitrary concurrent request.

## Reproduction scenario

```
Timeline (two concurrent requests to the same toWebHandler endpoint):

T0: Request A arrives → POST handler → webHandler(requestA)
    → Promise executor runs synchronously
    → httpRuntime.context set to A's context
    → fiber A forked, runs first ops synchronously
    → fiber A yields (e.g., at Effect.tryPromise boundary)
    → scheduler.scheduleTask(fiberA_continuation)
    → running=false → starve() called → Promise.resolve().then(drain)
       ↑ ALS context captured = Request A's context

T1: Request B arrives → POST handler → webHandler(requestB)
    → Promise executor runs synchronously
    → httpRuntime.context set to B's context
    → fiber B forked, runs first ops synchronously
    → fiber B yields
    → scheduler.scheduleTask(fiberB_continuation)
    → running=true → task queued, no new starve()

T2: Microtask fires → starveInternal() runs
    → Drains fiberA_continuation → auth() reads ALS → gets A's context ✓
    → Drains fiberB_continuation → auth() reads ALS → gets A's context ✗ ← WRONG USER
```

## Minimal reproduction

```typescript
import { AsyncLocalStorage } from "node:async_hooks"
import { Effect, Layer } from "effect"
import { RpcServer, RpcSerialization, Rpc, RpcGroup } from "@effect/rpc"
import { HttpServer } from "@effect/platform"
import * as S from "effect/Schema"

// Simulate a framework's ALS (like Next.js / Clerk)
const requestStore = new AsyncLocalStorage<{ userId: string }>()

class GetUser extends Rpc.make("GetUser", {
  success: S.Struct({ userId: S.String, alsUserId: S.String }),
  failure: S.Never,
  payload: {}
}) {}

const MyRpc = RpcGroup.make("MyRpc").add(GetUser)

const MyRpcLive = MyRpc.toLayer(
  RpcGroup.toHandlers(MyRpc, {
    GetUser: () =>
      Effect.gen(function*() {
        // Simulate calling an ALS-dependent API inside an Effect fiber
        const alsResult = yield* Effect.tryPromise({
          try: async () => {
            const store = requestStore.getStore()
            return store?.userId ?? "NONE"
          },
          catch: () => { throw new Error("impossible") }
        })
        return { userId: "from-effect-context", alsUserId: alsResult }
      })
  })
)

const RpcLayer = MyRpcLive.pipe(
  Layer.provideMerge(RpcSerialization.layerJson),
  Layer.provideMerge(HttpServer.layerContext)
)

const { handler } = RpcServer.toWebHandler(MyRpc, { layer: RpcLayer })

// Simulate two concurrent requests with different ALS contexts
async function main() {
  const results = await Promise.all([
    requestStore.run({ userId: "user-A" }, () => handler(makeRpcRequest("GetUser"))),
    requestStore.run({ userId: "user-B" }, () => handler(makeRpcRequest("GetUser"))),
  ])

  // Parse responses and check if alsUserId matches the expected user
  // Under the bug: both responses may show "user-A" (or one shows the other's)
  for (const res of results) {
    console.log(await res.json())
  }
}
```

## Impact

| Symptom | Severity |
|---------|----------|
| `auth()` returns wrong user's session | **Critical** — authentication bypass |
| `cookies()` / `headers()` from Next.js read wrong request | **High** — data leakage |
| OpenTelemetry trace context crosses requests | **Medium** — incorrect traces |
| Works locally, fails in production | Hard to diagnose — only manifests under concurrent load |

## Workaround

Capture ALS-dependent values **before** entering the Effect runtime and pass them via Effect's own context system:

```typescript
// In the route handler — OUTSIDE the Effect fiber (ALS is correct here)
export const POST = async (request: Request) => {
  const { userId } = await auth()  // ← Safe: still in Next.js ALS context

  // Inject into request headers or use the `context` parameter
  const headers = new Headers(request.headers)
  headers.set("x-clerk-auth-user-id", userId ?? "")
  const enrichedRequest = new Request(request.url, {
    method: request.method,
    headers,
    body: request.body,
    duplex: "half" as any,
  })

  return webHandler(enrichedRequest)
}

// In Effect handlers — read from HttpServerRequest headers instead of calling auth()
const getAuthenticatedUserId = Effect.gen(function*() {
  const req = yield* HttpServerRequest.HttpServerRequest
  const userId = req.headers["x-clerk-auth-user-id"]
  if (!userId) return yield* Effect.fail(new UnauthorizedError({ message: "Auth required" }))
  return userId
})
```

## Suggested fix (for Effect maintainers)

### Option A: Propagate ALS context through the scheduler

Capture the `AsyncLocalStorage` snapshot when a fiber continuation is scheduled, and restore it when the continuation executes:

```typescript
// In MixedScheduler or the fiber runtime
import { AsyncLocalStorage } from "node:async_hooks"

scheduleTask(task: Task, priority: number) {
  // Capture current ALS context
  const snapshot = AsyncLocalStorage.snapshot()
  this.tasks.scheduleTask(() => snapshot(task), priority)
  // ...
}
```

`AsyncLocalStorage.snapshot()` (Node.js 20.5+) returns a function that, when called, restores the ALS context from the point of capture. This ensures each fiber continuation runs with its originating request's ALS context.

**Trade-off:** Adds one closure allocation per scheduled task. Could be opt-in via a `FiberRef` or scheduler option.

### Option B: Capture ALS at `runFork` and restore per fiber step

When `Runtime.runFork` is called, capture the ALS snapshot and associate it with the fiber. Before each fiber step (in the fiber runtime's `evaluateEffect` loop), restore the snapshot.

**Trade-off:** More invasive but provides correct ALS propagation for the fiber's entire lifetime, including across `flatMap` chains and `Effect.tryPromise` thunks.

### Option C: Document the limitation and provide a `context` injection API

If ALS propagation is intentionally not supported, document this prominently and provide a first-class API for `toWebHandler` to accept per-request context. The existing `context?: Context.Context<never>` parameter on the handler function partially addresses this, but it requires callers to know about the issue and manually extract values before entering Effect.

## Related

- Node.js `AsyncLocalStorage` docs: https://nodejs.org/api/async_context.html
- `AsyncLocalStorage.snapshot()`: https://nodejs.org/api/async_context.html#static-method-asynclocalstoragesnapshot
- Next.js uses ALS for `cookies()`, `headers()`, `auth()` in App Router
- Similar issue pattern in other fiber-based runtimes (e.g., ZIO has `FiberRef` propagation for this)


## POC replica of my setup

```
// Create web handler from Effect RPC
// sharedMemoMap ensures all RPC routes share the same connection pool
const { handler: webHandler, dispose } = RpcServer.toWebHandler(DemoRpc, {
  layer: RpcLayer,
  memoMap: sharedMemoMap,
});

/**
 * POST /api/rpc/demo
 */
export const POST = async (request: Request) => {
  return webHandler(request);
};

registerDispose(dispose);
```

### Used util functions

```

/**
 * Creates a dispose registry that collects dispose callbacks and runs them
 * when `runAll` is invoked. Handles both sync and async dispose functions,
 * catching errors to prevent one failing dispose from breaking others.
 *
 * @internal Exported for testing — use `registerDispose` in application code.
 */
export const makeDisposeRegistry = () => {
  const disposeFns: Array<() => void | Promise<void>> = []

  const runAll = () => {
    for (const fn of disposeFns) {
      try {
        const result = fn()
        if (result && typeof result.then === "function") {
          result.then(undefined, (err: unknown) => console.error("Dispose error:", err))
        }
      } catch (err) {
        console.error("Dispose error:", err)
      }
    }
  }

  const register = (dispose: () => void | Promise<void>) => {
    disposeFns.push(dispose)
  }

  return { register, runAll }
}

export const registerDispose: (dispose: () => void | Promise<void>) => void = globalValue(
  Symbol.for("@global/RegisterDispose"),
  () => {
    const registry = makeDisposeRegistry()

    if (typeof process !== "undefined") {
      process.once("beforeExit", registry.runAll)
    }

    return registry.register
  }
)
```

### The actual effect that was run within the RPC context that the bug was found

```
export const getAuthenticatedUserId: Effect.Effect<string, UnauthorizedError> =
  Effect.gen(function*() {
    const authResult = yield* Effect.tryPromise({
      try: async () => auth(),
      catch: () =>
        new UnauthorizedError({
          message: "Failed to get auth session"
        })
    })

    if (!authResult.userId) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message: "Authentication required"
        })
      )
    }

    return authResult.userId
  })
 ```

## References
- https://github.com/Effect-TS/effect/security/advisories/GHSA-38f7-945m-qr2g
- https://nvd.nist.gov/vuln/detail/CVE-2026-32887
- https://github.com/Effect-TS/effect
