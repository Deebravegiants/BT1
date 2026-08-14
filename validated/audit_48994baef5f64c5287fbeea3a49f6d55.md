## Title
Missing per-network `chainId` enforcement for EVM assets in Ledger transaction signing allows unvalidated/attacker-influenced chain binding - (File: `features/hw-ledger/src/module/assets/ethereum.ts`)

### Summary
The external report's bug class is: a security-critical external dependency/mapping (`OPERATOR_FILTER_REGISTRY`) is not guaranteed to exist for every network, and the contract has no explicit check to guarantee its presence, silently degrading protection on "new" or unlisted networks. The `hydra` analog of this pattern is the hardcoded `assetName → chainId` map used when signing Ethereum-family transactions with a Ledger device: only `ethereum`, `matic`, and `basemainnet` are covered, with an explicit `// No default` fallthrough, meaning any other/new EVM network signed through this path has no chainId enforcement at all.

### Finding Description
In `createHandler` for the Ledger `ethereum` asset handler, `signTransaction` deserializes the raw transaction bytes and then attempts to force the correct `chainId` based on `params.assetName`: [1](#0-0) 

Only three assets are covered by this `switch` (`ethereum`→1, `matic`→137, `basemainnet`→8453), and the switch has an explicit `// No default` comment indicating this was intentional, not an oversight caught during review. Exodus, however, supports many more EVM networks that share the same Ledger Ethereum-app signing path, as documented in the provider docs (Optimism 10, Flare 14, Rootstock 30, BSC 56, Ethereum Classic 61, Fantom 250, Arbitrum One 42161, Arbitrum Nova 42170, Avalanche C 43114, Aurora 1313161554): [2](#0-1) 

For every one of these `assetName`s not present in the `switch`, `deserializedTransaction.chainId` is left as whatever value was already present in `params.signableTransaction` — i.e., whatever the upstream transaction-construction/signing pipeline (`tx-signer`/`transaction-signer.ts` → hardware signer) put there, without any assertion that it matches the network the wallet UI is presenting to the user for approval: [3](#0-2) 

This is directly analogous to the reported bug class: a protective mapping/registry (`chainId` enforcement per network) is assumed to exist for every network but is only populated for a subset, and there is no explicit guard (assertion/throw) to catch the "missing entry" case — the code just silently proceeds with an unverified value instead of failing safe.

### Impact Explanation
EIP-155 `chainId` is the mechanism that binds a signed Ethereum transaction to a specific chain and prevents replay across chains. If the chainId embedded in the raw transaction bytes going into the Ledger signing flow is incorrect or was not authoritatively re-derived from the intended asset/network for any of the EVM networks missing from this `switch`, the resulting signature is not guaranteed to be bound to the network the user believes they are transacting on. Combined with the fact that Exodus is documented as "stateless" with respect to active chain (each web3 site can request signing against a different chain, and the UI is the only cross-check a user has) — see: [4](#0-3) 

— a mismatch between the chain actually signed for and the chain intended/displayed can enable a signed transaction to be broadcast/replayed on a different chain than the user approved, i.e., a form of unauthorized-signing/cross-chain privilege bleed for hardware-wallet users signing on any EVM asset beyond `ethereum`, `matic`, and `basemainnet`.

### Likelihood Explanation
This code path executes on every hardware-wallet transaction signature for the affected assets; there is no error, warning, or telemetry indicating the missing case is being hit, matching the "silently degrades" nature of the original report. Because this is a hardcoded, unmaintained allowlist ("No default" explicitly documented as intentional), any newly-added EVM asset sharing the Ledger `ethereum` handler is affected by default unless a developer remembers to add a case — the exact same maintenance/deployment gap described in the original finding about `OPERATOR_FILTER_REGISTRY` not being deployed on new networks.

### Recommendation
Replace the allowlist `switch`/`No default` pattern with an explicit, fail-closed check: derive the expected `chainId` for `params.assetName` from a canonical asset/network registry, and throw if a mapping is not found rather than silently trusting whatever chainId is already present in `signableTransaction`. This guarantees every EVM asset signed via Ledger has its `chainId` authoritatively set/verified rather than depending on an incomplete manual list.

### Proof of Concept
1. Add or use an EVM asset supported by Exodus that is not one of `ethereum`, `matic`, `basemainnet` (e.g., `optimism`, `arbitrum`, `avalanche`) with a hardware (Ledger) wallet account.
2. Trigger a transaction sign request (e.g., via a connected dApp/web3 provider) whose `signableTransaction` payload contains a `chainId` different from the asset's real network id.
3. Observe in `signTransaction` (`features/hw-ledger/src/module/assets/ethereum.ts:109-131`) that the `switch` does not match, so `deserializedTransaction.chainId` is never corrected, and the Ledger device signs the transaction with the unmodified (attacker/dApp-supplied) `chainId`.
4. The resulting signature is valid for the chainId embedded in the payload, not necessarily the chain the user was shown/intended, demonstrating the missing enforcement.

### Citations

**File:** features/hw-ledger/src/module/assets/ethereum.ts (L109-131)
```typescript
      const deserializedTransaction = ethers.parse(params.signableTransaction)

      /** TODO: retrieve from meta or bubble this up to the asset library "signHardware" */
      switch (params.assetName) {
        case 'ethereum': {
          deserializedTransaction.chainId = 1

          break
        }

        case 'matic': {
          deserializedTransaction.chainId = 137

          break
        }

        case 'basemainnet': {
          deserializedTransaction.chainId = 8453

          break
        }
        // No default
      }
```

**File:** docs/web3-providers/ethereum-provider-api.md (L19-40)
```markdown
## Chain IDs

Exodus supports the following EVM chains out-of-the-box:

| Hex        | Decimal    | Network                  |
| ---------- | ---------- | ------------------------ |
| 0x1        | 1          | Ethereum Mainnet         |
| 0xa        | 10         | Optimism Mainnet         |
| 0xe        | 14         | Flare Mainnet            |
| 0x1e       | 30         | Rootstock Mainnet        |
| 0x38       | 56         | Binance Mainnet          |
| 0x3d       | 61         | Ethereum Classic Mainnet |
| 0x89       | 137        | Polygon Mainnet          |
| 0xfa       | 250        | Fantom Mainnet           |
| 0x2105     | 8453       | Base Mainnet             |
| 0xa4b1     | 42161      | Arbitrum One             |
| 0xa4ba     | 42170      | Arbitrum Nova            |
| 0xa86a     | 43114      | Avalanche C              |
| 0x4e454152 | 1313161554 | Aurora Mainnet           |

Adding chains dynamically is not yet supported. However, the list of supported
chains is growing fast. Stay tuned!
```

**File:** features/tx-signer/src/module/transaction-signer.ts (L29-55)
```typescript
  #getTransactionSigner = async (walletAccount: WalletAccount): Promise<InternalSigner> => {
    if (walletAccount.isSoftware) {
      return this.#seedBasedTransactionSigner
    }

    if (walletAccount.isHardware && this.#hardwareWallets) {
      return this.#hardwareWallets.requireDeviceFor(walletAccount)
    }

    throw new UnsupportedWalletAccountSource(walletAccount.source)
  }

  signTransaction = async (opts: SignTransactionParams) => {
    assert(typeof opts === 'object', `signTransaction expected parameters`)
    const { baseAssetName, unsignedTx, walletAccount } = opts
    assert(typeof baseAssetName === 'string', `baseAssetName must be string`)
    assert(typeof unsignedTx === 'object', `unsignedTx must be object`)
    const { txData, txMeta } = unsignedTx
    assert(typeof txData === 'object' && txData !== null, `txData must be object`)
    assert(typeof txMeta === 'object' && txMeta !== null, `txMeta must be object`)
    const signer = await this.#getTransactionSigner(walletAccount)
    return signer.signTransaction({
      baseAssetName,
      unsignedTx,
      walletAccount,
    })
  }
```

**File:** docs/web3-providers/ethereum-rpc-api.md (L51-58)
```markdown
Switches to the chain with the specified chain ID.

Unlike other wallets like MetaMask, Exodus is stateless. This means that there
is no concept of "active chain" at the wallet level. When a web3 site requests
switching the chain, the change only affects that site. Switching to a different
chain does not prompt the user for confirmation. Instead, the "active chain"
(from the web3 site's point of view) is displayed when asking for approval when
signing transactions or messages.
```
