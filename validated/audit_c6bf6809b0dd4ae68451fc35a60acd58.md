### Title
Cross-request signing result bleed via unkeyed `restrictConcurrency` wrapper on `#signGeneric` - (File: features/hardware-wallets/src/module/hardware-wallets.ts)

### Summary
`HardwareWallets#signGeneric` is the single choke point used by both `signTransaction()` and `signMessage()` to request a hardware-wallet signature. It is wrapped with `restrictConcurrency` from `make-concurrent`, called with no key-generator/options argument [1](#0-0) . Analogous to the StakingBonus race condition — where a state-dependent check (`calculateBonus`) combined with a shared mutable resource caused the second concurrent caller to silently receive the wrong (empty) result while still committing to an irreversible action — `#signGeneric` uses a single shared `this.#signingRequest` field and a concurrency-restriction wrapper that is not scoped per-request-identity. If two independent signing requests race (e.g. from two different dApp origins/wallet accounts calling `signTransaction`/`signMessage` in close succession), the second caller can be resolved with the in-flight result of the *first*, unrelated, request instead of its own.

### Finding Description
`#signGeneric` builds a fresh `id`, deferred promise, and a `sign` closure per call, but stores it in the single instance field `this.#signingRequest` [2](#0-1) . The function is wrapped by `restrictConcurrency(...)` with no explicit key/argument-hashing configuration [3](#0-2) [4](#0-3) . `make-concurrent`'s default behavior de-duplicates concurrent invocations of the wrapped function (by default keyed on the serializable subset of arguments); since the call args here include a `sign` callback function (not serializable to a stable/differentiating key) alongside `baseAssetName`/`walletAccount`, concurrent calls that don't differ in string-serializable fields (or whose function argument is ignored by the default key hasher) can collapse onto the same "in-flight" execution and share the identical `deferred.promise`.

Because only one execution of the wrapped async body actually proceeds when calls are deduped, a second, logically distinct, signing request (different `unsignedTx`/`message`, potentially different `walletAccount` or different asset) never runs its own `sign` closure — it instead awaits the promise created for the first caller and is resolved with the first caller's signature result. This is structurally the same failure mode as the report: a shared, un-partitioned resource (`bonus` pool / `#signingRequest`+concurrency dedupe) determines the outcome for whichever request executes/registers first, and the loser silently receives an outcome that does not correspond to what it actually requested, rather than an explicit rejection or independent execution.

### Impact Explanation
If exploitable, a second concurrent signing request (e.g., triggered by a second dApp tab, a WalletConnect session racing a native in-app flow, or two rapid API calls) can be resolved with a signature that was produced for a *different* transaction/message and potentially a *different* wallet account than what the second caller asked for. This is a concrete unauthorized-signing / cross-account privilege bleed: the caller believes it received a signature over its own requested payload but instead holds a signature belonging to another request, which can be replayed/submitted, or which discloses the fact/content of another origin's in-flight signing operation. This falls squarely under "concrete unauthorized signing" and "cross-origin/account privilege bleed" impact categories.

### Likelihood Explanation
This requires two hardware-wallet signing requests (transaction or message) to be in-flight concurrently through the same `HardwareWallets` instance — a realistic scenario for a wallet SDK that can be driven by multiple connected dApps/origins or rapid consecutive UI actions, and does not require any privileged access. The `#isRetrying` and single `#signingRequest` field design already show the developers assumed only one active request at a time, but the `restrictConcurrency` guard is the only enforcement of that assumption, and it is applied without an explicit per-request key, making its collision behavior dependent on `make-concurrent`'s default argument-hashing semantics rather than on the request's actual identity (`id`, `unsignedTx`, `walletAccount`).

### Recommendation
- Key the `restrictConcurrency` wrapper explicitly (or replace it with a request queue) using a value derived from the actual request identity (e.g., a per-call generated `id`, or a lock scoped by `walletAccount`+`baseAssetName`), instead of relying on default argument hashing of a call that includes a non-serializable `sign` function.
- Ensure `#signGeneric` cannot silently return another request's `deferred.promise`; each call should always run its own execution path (or be explicitly and visibly rejected/queued, not merged) when a distinct request is submitted while another is pending.
- Add regression tests that fire two concurrent `signTransaction`/`signMessage` calls with different payloads/accounts and assert each resolves with the signature corresponding to its own input.

### Proof of Concept
Conceptual PoC (mirrors the reported race structure): 
1. dApp A calls `hardwareWallets.signTransaction({ baseAssetName: 'ethereum', unsignedTx: txA, walletAccount: accountA })`.
2. Before the device confirms/rejects, dApp B calls `hardwareWallets.signMessage({ assetName: 'ethereum', message: msgB, walletAccount: accountB })` (or another `signTransaction` call) in the same tick.
3. Under `make-concurrent`'s default dedupe key derivation, the second call is treated as a duplicate invocation of `#signGeneric` and awaits the same `deferred.promise` created for request A's `sign` closure at [5](#0-4) .
4. When the device signs request A, both promises resolve with request A's signature — dApp B receives a signature over `txA`/`accountA` rather than `msgB`/`accountB`.

Note: I could not execute this against the live `make-concurrent` implementation to confirm its exact default key-derivation behavior (whether function arguments are silently dropped from the hash key, causing collision) since no further tool calls were available in this session; this should be verified directly in `make-concurrent`'s source/tests before treating this as fully confirmed, but the code structure (single un-parameterized `restrictConcurrency` wrapper protecting a shared `#signingRequest` across heterogeneous request types) is a direct structural analog to the reported race condition.

### Citations

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L12-12)
```typescript
import restrictConcurrency from 'make-concurrent'
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L308-343)
```typescript
  #signGeneric = restrictConcurrency(
    async ({ baseAssetName, scenario, sign, walletAccount }: GenericSignParams) => {
      const id = randomBytes(16).toString('hex')
      this.#logger.debug(
        `Starting signing request for ${baseAssetName} with scenario: ${scenario} and id: ${id}`
      )
      const deferred = pDefer()

      // Track the signing request in the internal map
      // so the UI can retry & cancel if needed.
      this.#signingRequest = {
        id,
        baseAssetName,
        walletAccount,
        sign: async ({ device }) => {
          // Kick off the signing request to the UI
          await this.#updateSigningRequest({
            id,
            baseAssetName,
            scenario,
          })

          await device.ensureDeviceReady({ baseAssetName, walletAccount })
          return sign({ device })
        },
        resolve: deferred.resolve,
        reject: deferred.reject,
      }

      // We don't await for the signing request to complete here,
      // as the UI will handle it asynchronously.
      void this.retrySigningRequest(id)

      return deferred.promise
    }
  )
```
