# [?] fix(connectors): remove ledger due to security vulnerability

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/wagmi
Published: 2023-12-14
Source: https://github.com/wevm/wagmi/commit/53ca1f7eb411d912e11fcce7e03bd61ed067959c
Type: security-commit

## Details
fix(connectors): remove ledger due to security vulnerability

## Patch
### .changeset/grumpy-pears-obey.md
```diff
@@ -0,0 +1,7 @@
+---
+"@wagmi/connectors": patch
+"@wagmi/core": patch
+"wagmi": patch
+---
+
+Removed LedgerConnector due to security vulnerability
```

### docs/pages/core/connectors/_meta.en-US.json
```diff
@@ -1,7 +1,6 @@
 {
   "injected": "Injected",
   "coinbaseWallet": "Coinbase Wallet",
-  "ledger": "Ledger",
   "metaMask": "MetaMask",
   "mock": "Mock",
   "safe": "Safe",
```

### docs/pages/core/connectors/ledger.en-US.mdx
```diff
@@ -1,133 +0,0 @@
----
-title: 'Ledger Wallet'
-description: 'Official wagmi Connector for Ledger.'
----
-
-# Ledger
-
-The `LedgerConnector` supports connecting with a Ledger device using the [Ledger Connect Kit](https://developers.ledger.com/docs/connect/introduction/).
-
-```ts
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-```
-
-## Usage 
-
-### WalletConnect v2
-
-To get started with Ledger + WalletConnect v2, you will need to retrieve a Project ID. You can find your Project ID [here](https://cloud.walletconnect.com/sign-in).
-
-```ts
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-import { mainnet } from '@wagmi/core/chains'
-
-const connector = new LedgerConnector({
-  chains: [mainnet],
-  projectId: '...',
-})
-```
-
-Note: The above example is using chains from [`@wagmi/core/chains` entrypoint](/react/chains#wagmichains).
-
-### WalletConnect v1
-
-```ts
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-import { mainnet } from '@wagmi/core/chains'
-
-const connector = new LedgerConnector({
-  chains: [mainnet],
-})
-```
-
-## Configuration
-
-### chains (optional)
-
-Chains supported by app. Defaults to `defaultChains`.
-
-```ts {5}
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-import { mainnet } from '@wagmi/core/chains'
-
-const connector = new LedgerConnector({
-  chains: [mainnet],
-})
-```
-
-### options (WalletConnect v2)
-
-#### projectId
-
-WalletConnect Cloud Project ID. You can find your Project ID [here](https://cloud.walletconnect.com/sign-in).
-
-```ts {5}
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    projectId: '...',
-  },
-})
-```
-
-#### enableDebugLogs
-
-Toggle debug logging for Ledger Connect Kit.
-
-```ts {6}
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    projectId: '...',
-    enableDebugLogs: true,
-  },
-})
-```
-
-### options (WalletConnect v1)
-
-#### chainId
-
-The Chain ID of the connecting chain.
-
-```ts {5}
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    chainId: 1,
-  },
-})
-```
-
-#### enableDebugLogs
-
-Toggle debug logging for Ledger Connect Kit.
-
-```ts {5}
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    enableDebugLogs: true,
-  },
-})
-```
-
-#### rpc
-
-A Chain ID (key) / RPC URL (value) map.
-
-```ts {5-7}
-import { LedgerConnector } from '@wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    rpc: {
-      1: 'https://eth-mainnet.alchemyapi.io/v2/yourAlchemyId',
-    },
-  },
-})
-```
```

### docs/pages/react/connectors/_meta.en-US.json
```diff
@@ -1,7 +1,6 @@
 {
   "injected": "Injected",
   "coinbaseWallet": "Coinbase Wallet",
-  "ledger": "Ledger",
   "metaMask": "MetaMask",
   "mock": "Mock",
   "safe": "Safe",
```

### docs/pages/react/connectors/ledger.en-US.mdx
```diff
@@ -1,133 +0,0 @@
----
-title: 'Ledger Wallet'
-description: 'Official wagmi Connector for Ledger.'
----
-
-# Ledger
-
-The `LedgerConnector` supports connecting with a Ledger device using the [Ledger Connect Kit](https://developers.ledger.com/docs/connect/introduction/).
-
-```ts
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-```
-
-## Usage 
-
-### WalletConnect v2
-
-To get started with Ledger + WalletConnect v2, you will need to retrieve a Project ID. You can find your Project ID [here](https://cloud.walletconnect.com/sign-in).
-
-```ts
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-import { mainnet } from '@wagmi/core/chains'
-
-const connector = new LedgerConnector({
-  chains: [mainnet],
-  projectId: '...',
-})
-```
-
-Note: The above example is using chains from [`@wagmi/core/chains` entrypoint](/react/chains#wagmichains).
-
-### WalletConnect v1
-
-```ts
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-import { mainnet } from '@wagmi/core/chains'
-
-const connector = new LedgerConnector({
-  chains: [mainnet],
-})
-```
-
-## Configuration
-
-### chains (optional)
-
-Chains supported by app. Defaults to `defaultChains`.
-
-```ts {5}
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-import { mainnet } from '@wagmi/core/chains'
-
-const connector = new LedgerConnector({
-  chains: [mainnet],
-})
-```
-
-### options (WalletConnect v2)
-
-#### projectId
-
-WalletConnect Cloud Project ID. You can find your Project ID [here](https://cloud.walletconnect.com/sign-in).
-
-```ts {5}
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    projectId: '...',
-  },
-})
-```
-
-#### enableDebugLogs
-
-Toggle debug logging for Ledger Connect Kit.
-
-```ts {6}
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    projectId: '...',
-    enableDebugLogs: true,
-  },
-})
-```
-
-### options (WalletConnect v1)
-
-#### chainId
-
-The Chain ID of the connecting chain.
-
-```ts {5}
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    chainId: 1,
-  },
-})
-```
-
-#### enableDebugLogs
-
-Toggle debug logging for Ledger Connect Kit.
-
-```ts {5}
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    enableDebugLogs: true,
-  },
-})
-```
-
-#### rpc
-
-A Chain ID (key) / RPC URL (value) map.
-
-```ts {5-7}
-import { LedgerConnector } from 'wagmi/connectors/ledger'
-
-const connector = new LedgerConnector({
-  options: {
-    rpc: {
-      1: 'https://eth-mainnet.alchemyapi.io/v2/yourAlchemyId',
-    },
-  },
-})
-```
```

### examples/_dev/src/pages/_app.tsx
```diff
@@ -5,7 +5,6 @@ import { avalanche, goerli, mainnet, optimism } from 'wagmi/chains'
 
 import { CoinbaseWalletConnector } from 'wagmi/connectors/coinbaseWallet'
 import { InjectedConnector } from 'wagmi/connectors/injected'
-import { LedgerConnector } from 'wagmi/connectors/ledger'
 import { MetaMaskConnector } from 'wagmi/connectors/metaMask'
 import { SafeConnector } from 'wagmi/connectors/safe'
 import { WalletConnectConnector } from 'wagmi/connectors/walletConnect'
@@ -51,12 +50,6 @@ const config = createConfig({
         qrcode: true,
       },
     }),
-    new LedgerConnector({
-      chains,
-      options: {
-        projectId: process.env.NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID ?? '',
-      },
-    }),
     new InjectedConnector({
       chains,
       options: {
```

### packages/connectors/.gitignore
```diff
@@ -1,7 +1,6 @@
 # Generated file. Do not edit directly.
 coinbaseWallet/**
 injected/**
-ledger/**
 metaMask/**
 mock/**
 safe/**
```

### packages/connectors/README.md
```diff
@@ -35,7 +35,6 @@ const config = createConfig({
 
 - [`CoinbaseWalletConnector`](/packages/connectors/src/coinbaseWallet.ts)
 - [`InjectedConnector`](/packages/connectors/src/injected.ts)
-- [`LedgerConnector`](/packages/connectors/src/ledger.ts)
 - [`MetaMaskConnector`](/packages/connectors/src/metaMask.ts)
 - [`MockConnector`](/packages/connectors/src/mock.ts)
 - [`SafeConnector`](/packages/connectors/src/safe.ts)
```

### packages/connectors/package.json
```diff
@@ -18,7 +18,6 @@
   },
   "dependencies": {
     "@coinbase/wallet-sdk": "^3.6.6",
-    "@ledgerhq/connect-kit-loader": "^1.1.0",
     "@safe-global/safe-apps-provider": "^0.18.1",
     "@safe-global/safe-apps-sdk": "^8.1.0",
     "@walletconnect/ethereum-provider": "2.10.6",
@@ -47,10 +46,6 @@
       "types": "./dist/injected.d.ts",
       "default": "./dist/injected.js"
     },
-    "./ledger": {
-      "types": "./dist/ledger.d.ts",
-      "default": "./dist/ledger.js"
-    },
     "./metaMask": {
       "types": "./dist/metaMask.d.ts",
       "default": "./dist/metaMask.js"
@@ -76,7 +71,6 @@
   "files": [
     "/coinbaseWallet",
     "/injected",
-    "/ledger",
     "/metaMask",
     "/mock",
     "/safe",
```

### packages/connectors/src/ledger.test.ts
```diff
@@ -1,74 +0,0 @@
-import { describe, expect, it } from 'vitest'
-
-import { testChains } from '../test'
-import { LedgerConnector } from './ledger'
-
-/*
- * To manually test the Ledger connector:
- *
- * - install the Ledger Live app, https://www.ledger.com/ledger-live
- * - install the Ledger Connect extension, currently in beta, it should soon be
- *   distributed with the Ledger Live app for iOS and macOS
- * - run the wagmi playground app following the contributing docs on the main
- *   wagmi repository
- * - open the playground app in a web browser
- * - press the "Ledger" button
- * - see below for the Ledger Connect and Ledger Live flows
- * - after the account is selected on the wallet the dapp state should reflect
- *   the chosen account information
- *
- * Ledger Connect
- *
- * - if you are on a platform supported by the Ledger Connect extension
- *   (currently Safari on iOS and macOS) but don't have it installed or enabled
- *   you should see a modal explaining how you can do that
- * - if you are on a platform supported by the Ledger Connect extension and
- *   have it installed and enabled it should pop up allowing you to select an
- *   account
- *   - when pressing the "Disconnect" button on the dapp, the dapp shows as
- *     disconnected but you are not actually disconnected until you press
- *     the "Disconnect" button on Ledger Connect
- *   - when pressing the "Disconnect" button on Ledger Connect (press the pill
- *     shaped button with the Ledger logo, then "Disconnect" on the popup), the
- *     dapp should also show as disconnected
- *
- * Testing Ledger Live
- *
- * - if you are on a platform not yet supported by the Connect extension you
- *   should see a modal allowing you to use the Ledger Live app; pressing
- *   "Use Ledger Live" or scanning the QR code should open the app and allow
- *   you to choose an account
- *   - when pressing the "Disconnect" button on the dapp, Ledger Live should
- *     also show as disconnected
- *   - when pressing the "Disconnect" button on Ledger Live, the dapp should
- *     also show as disconnected
- *   - when switching accounts on Ledger Live the dapp should reflect those
- *     changes
- */
-describe('LedgerConnector', () => {
-  it('inits', () => {
-    const connector = new LedgerConnector({
-      chains: testChains,
-      options: {},
-    })
-    expect(connector.name).toEqual('Ledger')
-  })
-
-  describe('behavior', () => {
-    it.todo('connects')
-
-    it.todo('disconnects via dapp (wagmi Connector)')
-
-    it.todo('disconnects via wallet (Ledger Live)')
-
-    it.todo('switch chains via dapp (wagmi Connector)')
-
-    it.todo('switch chains via wallet (Ledger Live)')
-
-    it.todo('switch accounts via wallet (Ledger Live)')
-
-    it.todo('sends a transaction')
-
-    it.todo('signs a message')
-  })
-})
```

### packages/connectors/src/ledger.ts
```diff
@@ -1,310 +0,0 @@
-import {
-  EthereumProvider,
-  SupportedProviders,
-  loadConnectKit,
-} from '@ledgerhq/connect-kit-loader'
-import { EthereumProviderOptions } from '@walletconnect/ethereum-provider/dist/types/EthereumProvider'
-import {
-  ProviderRpcError,
-  SwitchChainError,
-  UserRejectedRequestError,
-  createWalletClient,
-  custom,
-  getAddress,
-  numberToHex,
-} from 'viem'
-import type { Chain } from 'viem/chains'
-
-import { Connector } from './base'
-import type { WalletClient } from './types'
-import { normalizeChainId } from './utils/normalizeChainId'
-
-type LedgerConnectorWcV1Options = {
-  walletConnectVersion?: 1
-  bridge?: string
-  chainId?: number
-  projectId?: never
-  rpc?: { [chainId: number]: string }
-}
-
-type LedgerConnectorWcV2Options = {
-  walletConnectVersion?: 2
-  projectId?: EthereumProviderOptions['projectId']
-  requiredChains?: number[]
-  requiredMethods?: string[]
-  optionalMethods?: string[]
-  requiredEvents?: string[]
-  optionalEvents?: string[]
-}
-
-type LedgerConnectorOptions = {
-  enableDebugLogs?: boolean
-} & (LedgerConnectorWcV1Options | LedgerConnectorWcV2Options)
-
-type ConnectConfig = {
-  /** Target chain to connect to. */
-  chainId?: number
-}
-
-export class LedgerConnector extends Connector<
-  EthereumProvider,
-  LedgerConnectorOptions
-> {
-  readonly id = 'ledger'
-  readonly name = 'Ledger'
-  readonly ready = true
-
-  #provider?: EthereumProvider
-  #initProviderPromise?: Promise<void>
-  #isV1: boolean
-
-  get walletConnectVersion(): 1 | 2 {
-    if (this.options.walletConnectVersion)
-      return this.options.walletConnectVersion
-    else if ((this.options as LedgerConnectorWcV2Options).projectId) return 2
-    return 1
-  }
-
-  constructor(config: { chains?: Chain[]; options: LedgerConnectorOptions }) {
-    super({
-      ...config,
-      options: { ...config.options },
-    })
-
-    this.#isV1 = this.walletConnectVersion === 1
-  }
-
-  async connect({ chainId }: ConnectConfig = {}) {
-    try {
-      const provider = await this.getProvider({ create: true })
-      this.#setupListeners()
-
-      // Don't request accounts if we have a session, like when reloading with
-      // an active WC v2 session
-      if (!provider.session) {
-        this.emit('message', { type: 'connecting' })
-
-        await provider.request({
-          method: 'eth_requestAccounts',
-        })
-      }
-
-      const account = await this.getAccount()
-      let id = await this.getChainId()
-      let unsupported = this.isChainUnsupported(id)
-
-      if (chainId && id !== chainId) {
-        const chain = await this.switchChain(chainId)
-        id = chain.id
-        unsupported = this.isChainUnsupported(id)
-      }
-
-      return {
-        account,
-        chain: { id, unsupported },
-        provider,
-      }
-    } catch (error) {
-      if (/user rejected/i.test((error as ProviderRpcError)?.message)) {
-        throw new UserRejectedRequestError(error as Error)
-      }
-      throw error
-    }
-  }
-
-  async disconnect() {
-    const provider = await this.getProvider()
-    try {
-      if (provider?.disconnect) await provider.disconnect()
-    } catch (error) {
-      if (!/No matching key/i.test((error as Error).message)) throw error
-    } finally {
-      this.#removeListeners()
-
-      this.#isV1 &&
-        typeof localStorage !== 'undefined' &&
-        localStorage.removeItem('walletconnect')
-    }
-  }
-
-  async getAccount() {
-    const provider = await this.getProvider()
-    const accounts = (await provider.request({
-      method: 'eth_accounts',
-    })) as string[]
-    const account = getAddress(accounts[0] as string)
-
-    return account
-  }
-
-  async getChainId() {
-    const provider = await this.getProvider()
-    const chainId = (await provider.request({
-      method: 'eth_chainId',
-    })) as number
-
-    return normalizeChainId(chainId)
-  }
-
-  async getProvider(
-    { chainId, create }: { chainId?: number; create?: boolean } = {
-      create: false,
-    },
-  ) {
-    if (!this.#provider || (this.#isV1 && create)) {
-      await this.#createProvider()
-    }
-    if (chainId) await this.switchChain(chainId)
-    return this.#provider!
-  }
-
-  async getWalletClient({
-    chainId,
-  }: { chainId?: number } = {}): Promise<WalletClient> {
-    const [provider, account] = await Promise.all([
-      this.getProvider({ chainId }),
-      this.getAccount(),
-    ])
-    const chain = this.chains.find((x) => x.id === chainId)
-
-    if (!provider) throw new Error('provider is required.')
-    return createWalletClient({ account, chain, transport: custom(provider) })
-  }
-
-  async isAuthorized() {
-    try {
-      const account = await this.getAccount()
-
-      return !!account
-    } catch {
-      return false
-    }
-  }
-
-  async switchChain(chainId: number) {
-    const chain = this.chains.find((chain) => chain.id === chainId)
-    if (!chain)
-      throw new SwitchChainError(new Error('chain not found on connector.'))
-
-    try {
-      const provider = await this.getProvider()
-
-      await provider.request({
-        method: 'wallet_switchEthereumChain',
-        params: [{ chainId: numberToHex(chainId) }],
-      })
-
-      return chain
-    } catch (error) {
-      const message =
-        typeof error === 'string' ? error : (error as ProviderRpcError)?.message
-      if (/user rejected request/i.test(message)) {
-        throw new UserRejectedRequestError(error as Error)
-      }
-      throw new SwitchChainError(error as Error)
-    }
-  }
-
-  async #createProvider() {
-    if (!this.#initProviderPromise && typeof window !== 'undefined') {
-      this.#initProviderPromise = this.#initProvider()
-    }
-    return this.#initProviderPromise
-  }
-
-  async #initProvider() {
-    const connectKit = await loadConnectKit()
-
-    if (this.options.enableDebugLogs) {
-      connectKit.enableDebugLogs()
-    }
-
-    let checkSupportOptions
-
-    if (this.#isV1) {
-      const { chainId, bridge } = this.options as LedgerConnectorWcV1Options
-      checkSupportOptions = {
-        providerType: SupportedProviders.Ethereum,
-        walletConnectVersion: 1,
-        chainId,
-        bridge,
-        rpc: Object.fromEntries(
-          this.chains.map((chain) => [
-            chain.id,
-            chain.rpcUrls.default.http[0]!,
-          ]),
-        ),
-      }
-    } else {
-      const {
-        projectId,
-        requiredChains,
-        requiredMethods,
-        optionalMethods,
-        requiredEvents,
-        optionalEvents,
-      } = this.options as LedgerConnectorWcV2Options
-      const optionalChains = this.chains.map(({ id }) => id)
-
-      checkSupportOptions = {
-        providerType: SupportedProviders.Ethereum,
-        walletConnectVersion: 2,
-        projectId,
-        chains: requiredChains,
-        optionalChains,
-        methods: requiredMethods,
-        optionalMethods,
-        events: requiredEvents,
-        optionalEvents,
-        rpcMap: Object.fromEntries(
-          this.chains.map((chain) => [
-            chain.id,
-            chain.rpcUrls.default.http[0]!,
-          ]),
-        ),
-      }
-    }
-    connectKit.checkSupport(checkSupportOptions)
-
-    this.#provider =
-      (await connectKit.getProvider()) as unknown as EthereumProvider
-  }
-
-  #setupListeners() {
-    if (!this.#provider) return
-    this.#removeListeners()
-    this.#provider.on('accountsChanged', this.onAccountsChanged)
-    this.#provider.on('chainChanged', this.onChainChanged)
-    this.#provider.on('disconnect', this.onDisconnect)
-    this.#provider.on('session_delete', this.onDisconnect)
-    this.#provider.on('connect', this.onConnect)
-  }
-
-  #removeListeners() {
-    if (!this.#provider) return
-    this.#provider.removeListener('accountsChanged', this.onAccountsChanged)
-    this.#provider.removeListener('chainChanged', this.onChainChanged)
-    this.#provider.removeListener('disconnect', this.onDisconnect)
-    this.#provider.removeListener('session_delete', this.onDisconnect)
-    this.#provider.removeListener('connect', this.onConnect)
-  }
-
-  protected onAccountsChanged = (accounts: string[]) => {
-    if (accounts.length === 0) this.emit('disconnect')
-    else this.emit('change', { account: getAddress(accounts[0]!) })
-  }
-
-  protected onChainChanged = (chainId: number | string) => {
-    const id = normalizeChainId(chainId)
-    const unsupported = this.isChainUnsupported(id)
-    this.emit('change', { chain: { id, unsupported } })
-  }
-
-  protected onDisconnect = () => {
-    this.emit('disconnect')
-  }
-
-  protected onConnect = () => {
-    this.emit('connect', {})
-  }
-}
```

### packages/connectors/tsup.config.ts
```diff
@@ -10,7 +10,6 @@ export default defineConfig(
       'src/index.ts',
       'src/coinbaseWallet.ts',
       'src/injected.ts',
-      'src/ledger.ts',
       'src/metaMask.ts',
       'src/mock/index.ts',
       'src/safe.ts',
```
