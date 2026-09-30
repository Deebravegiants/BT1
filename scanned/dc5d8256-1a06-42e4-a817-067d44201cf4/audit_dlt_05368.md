# [?] feat(ironfish): Fix double spend issue in transaction expiration (#3523)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2023-02-27
Source: https://github.com/iron-fish/ironfish/commit/23e45af925b75437be0050762f41a443fa6a46c9
Type: security-commit

## Details
feat(ironfish): Fix double spend issue in transaction expiration (#3523)

* feat(ironfish): Create `nullifierToTransactionHash` store

* feat(ironfish): Create `nullifierToTransactionHash` store (#3518)

* feat(ironfish): Update nullifier to transaction hash store

* feat(ironfish): Check nullifier -> transaction hash befor marking notes as unspent (#3520)

* feat(ironfish): Backfill `nullifierToTransactionHash` (#3522)

* feat(ironfish): Backfill `nullifierToTransactionHash`

* refactor(ironfish): Clean up output string

* refactor(ironfish): Update log from assets

* fix(ironfish): Only add unspent note hash if expiring the tx

## Patch
### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash.ts
```diff
@@ -0,0 +1,101 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import { Logger } from '../../logger'
+import { IronfishNode } from '../../node'
+import { IDatabase, IDatabaseTransaction } from '../../storage'
+import { createDB } from '../../storage/utils'
+import { Account } from '../../wallet'
+import { Migration } from '../migration'
+import { GetStores } from './025-backfill-wallet-nullifier-to-transaction-hash/stores'
+
+export class Migration025 extends Migration {
+  path = __filename
+
+  prepare(node: IronfishNode): IDatabase {
+    return createDB({ location: node.config.walletDatabasePath })
+  }
+
+  async forward(
+    node: IronfishNode,
+    db: IDatabase,
+    _tx: IDatabaseTransaction | undefined,
+    logger: Logger,
+  ): Promise<void> {
+    const accounts = []
+    const stores = GetStores(db)
+
+    for await (const account of stores.old.accounts.getAllValuesIter()) {
+      accounts.push(
+        new Account({
+          ...account,
+          walletDb: node.wallet.walletDb,
+        }),
+      )
+    }
+
+    const accountsString =
+      accounts.length === 1 ? `${accounts.length} account` : `${accounts.length} accounts`
+    logger.info(`Backfilling nullifier to transaction hashes for ${accountsString}`)
+
+    for (const account of accounts) {
+      logger.info('')
+      logger.info(`  Backfilling nullifier to transaction hashes for account ${account.name}`)
+
+      const head = await stores.old.heads.get(account.id)
+      // If the account has not scanned, we can skip the backfill
+      if (!head) {
+        continue
+      }
+
+      let transactionCount = 0
+      for await (const { blockHash, transaction } of stores.old.transactions.getAllValuesIter(
+        undefined,
+        account.prefixRange,
+      )) {
+        // If the transaction is expired, we can skip the backfill
+        if (
+          !blockHash &&
+          transaction.expiration() !== 0 &&
+          transaction.expiration() <= head.sequence
+        ) {
+          continue
+        }
+
+        // Backfill the mappings from all transaction spends
+        for (const spend of transaction.spends) {
+          const existingNullifierToTransactionHash =
+            await stores.new.nullifierToTransactionHash.get([account.prefix, spend.nullifier])
+          // Upsert a record for connected transactions or if a mapping doesn't already exist
+          if (blockHash || !existingNullifierToTransactionHash) {
+            await stores.new.nullifierToTransactionHash.put(
+              [account.prefix, spend.nullifier],
+              transaction.hash(),
+            )
+          }
+        }
+
+        transactionCount++
+      }
+
+      const transactionsString =
+        transactionCount === 1
+          ? `${transactionCount} transaction`
+          : `${transactionCount} transactions`
+      logger.info(`  Completed backfilling ${transactionsString} for account ${account.name}`)
+    }
+
+    logger.info('')
+  }
+
+  async backward(
+    _node: IronfishNode,
+    db: IDatabase,
+    tx: IDatabaseTransaction | undefined,
+    logger: Logger,
+  ): Promise<void> {
+    const stores = GetStores(db)
+    logger.info('Clearing nullifierToTransactionHash')
+    await stores.new.nullifierToTransactionHash.clear(tx)
+  }
+}
```

### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash/new/index.ts
```diff
@@ -0,0 +1,20 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import { BufferEncoding, IDatabase, IDatabaseStore, PrefixEncoding } from '../../../../storage'
+
+export function GetNewStores(db: IDatabase): {
+  nullifierToTransactionHash: IDatabaseStore<{
+    key: [Buffer, Buffer]
+    value: Buffer
+  }>
+} {
+  const nullifierToTransactionHash: IDatabaseStore<{ key: [Buffer, Buffer]; value: Buffer }> =
+    db.addStore({
+      name: 'nt',
+      keyEncoding: new PrefixEncoding(new BufferEncoding(), new BufferEncoding(), 4),
+      valueEncoding: new BufferEncoding(),
+    })
+
+  return { nullifierToTransactionHash }
+}
```

### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash/old/accountValue.ts
```diff
@@ -0,0 +1,84 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import { PUBLIC_ADDRESS_LENGTH } from '@ironfish/rust-nodejs'
+import bufio from 'bufio'
+import { IDatabaseEncoding } from '../../../../storage'
+
+const KEY_LENGTH = 32
+export const VIEW_KEY_LENGTH = 64
+const VERSION_LENGTH = 2
+
+export interface AccountValue {
+  version: number
+  id: string
+  name: string
+  spendingKey: string | null
+  viewKey: string
+  incomingViewKey: string
+  outgoingViewKey: string
+  publicAddress: string
+}
+
+export class AccountValueEncoding implements IDatabaseEncoding<AccountValue> {
+  serialize(value: AccountValue): Buffer {
+    const bw = bufio.write(this.getSize(value))
+    let flags = 0
+    flags |= Number(!!value.spendingKey) << 0
+    bw.writeU8(flags)
+    bw.writeU16(value.version)
+    bw.writeVarString(value.id, 'utf8')
+    bw.writeVarString(value.name, 'utf8')
+    if (value.spendingKey) {
+      bw.writeBytes(Buffer.from(value.spendingKey, 'hex'))
+    }
+    bw.writeBytes(Buffer.from(value.viewKey, 'hex'))
+    bw.writeBytes(Buffer.from(value.incomingViewKey, 'hex'))
+    bw.writeBytes(Buffer.from(value.outgoingViewKey, 'hex'))
+    bw.writeBytes(Buffer.from(value.publicAddress, 'hex'))
+
+    return bw.render()
+  }
+
+  deserialize(buffer: Buffer): AccountValue {
+    const reader = bufio.read(buffer, true)
+    const flags = reader.readU8()
+    const version = reader.readU16()
+    const hasSpendingKey = flags & (1 << 0)
+    const id = reader.readVarString('utf8')
+    const name = reader.readVarString('utf8')
+    const spendingKey = hasSpendingKey ? reader.readBytes(KEY_LENGTH).toString('hex') : null
+    const viewKey = reader.readBytes(VIEW_KEY_LENGTH).toString('hex')
+    const incomingViewKey = reader.readBytes(KEY_LENGTH).toString('hex')
+    const outgoingViewKey = reader.readBytes(KEY_LENGTH).toString('hex')
+    const publicAddress = reader.readBytes(PUBLIC_ADDRESS_LENGTH).toString('hex')
+
+    return {
+      version,
+      id,
+      name,
+      viewKey,
+      incomingViewKey,
+      outgoingViewKey,
+      spendingKey,
+      publicAddress,
+    }
+  }
+
+  getSize(value: AccountValue): number {
+    let size = 0
+    size += 1
+    size += VERSION_LENGTH
+    size += bufio.sizeVarString(value.id, 'utf8')
+    size += bufio.sizeVarString(value.name, 'utf8')
+    if (value.spendingKey) {
+      size += KEY_LENGTH
+    }
+    size += VIEW_KEY_LENGTH
+    size += KEY_LENGTH
+    size += KEY_LENGTH
+    size += PUBLIC_ADDRESS_LENGTH
+
+    return size
+  }
+}
```

### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash/old/headValue.ts
```diff
@@ -0,0 +1,43 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import bufio from 'bufio'
+import { IDatabaseEncoding } from '../../../../storage'
+
+export type HeadValue = {
+  hash: Buffer
+  sequence: number
+}
+
+export class NullableHeadValueEncoding implements IDatabaseEncoding<HeadValue | null> {
+  serialize(value: HeadValue | null): Buffer {
+    const bw = bufio.write(this.getSize(value))
+
+    if (value) {
+      bw.writeHash(value.hash)
+      bw.writeU32(value.sequence)
+    }
+
+    return bw.render()
+  }
+
+  deserialize(buffer: Buffer): HeadValue | null {
+    const reader = bufio.read(buffer, true)
+
+    if (reader.left()) {
+      const hash = reader.readHash()
+      const sequence = reader.readU32()
+      return { hash, sequence }
+    }
+
+    return null
+  }
+
+  getSize(value: HeadValue | null): number {
+    if (!value) {
+      return 0
+    }
+
+    return 32 + 4
+  }
+}
```

### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash/old/index.ts
```diff
@@ -0,0 +1,45 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import {
+  BufferEncoding,
+  IDatabase,
+  IDatabaseStore,
+  PrefixEncoding,
+  StringEncoding,
+} from '../../../../storage'
+import { AccountValue, AccountValueEncoding } from './accountValue'
+import { HeadValue, NullableHeadValueEncoding } from './headValue'
+import { TransactionValue, TransactionValueEncoding } from './transactionValue'
+
+export function GetOldStores(db: IDatabase): {
+  accounts: IDatabaseStore<{ key: string; value: AccountValue }>
+  heads: IDatabaseStore<{ key: string; value: HeadValue | null }>
+  transactions: IDatabaseStore<{ key: [Buffer, Buffer]; value: TransactionValue }>
+} {
+  const accounts: IDatabaseStore<{ key: string; value: AccountValue }> = db.addStore({
+    name: 'a',
+    keyEncoding: new StringEncoding(),
+    valueEncoding: new AccountValueEncoding(),
+  })
+
+  const heads: IDatabaseStore<{
+    key: string
+    value: HeadValue | null
+  }> = db.addStore({
+    name: 'h',
+    keyEncoding: new StringEncoding(),
+    valueEncoding: new NullableHeadValueEncoding(),
+  })
+
+  const transactions: IDatabaseStore<{
+    key: [Buffer, Buffer]
+    value: TransactionValue
+  }> = db.addStore({
+    name: 't',
+    keyEncoding: new PrefixEncoding(new BufferEncoding(), new BufferEncoding(), 4),
+    valueEncoding: new TransactionValueEncoding(),
+  })
+
+  return { accounts, heads, transactions }
+}
```

### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash/old/transactionValue.ts
```diff
@@ -0,0 +1,112 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import type { IDatabaseEncoding } from '../../../../storage/database/types'
+import { BufferMap } from 'buffer-map'
+import bufio from 'bufio'
+import { Transaction } from '../../../../primitives'
+
+const ASSET_ID_LENGTH = 32
+
+export interface TransactionValue {
+  transaction: Transaction
+  timestamp: Date
+  // These fields are populated once the transaction is on the main chain
+  blockHash: Buffer | null
+  sequence: number | null
+  // This is populated when we create a transaction to track when we should
+  // rebroadcast. This can be null if we created it on another node, or the
+  // transaction was created for us by another person.
+  submittedSequence: number
+  assetBalanceDeltas: BufferMap<bigint>
+}
+
+export class TransactionValueEncoding implements IDatabaseEncoding<TransactionValue> {
+  serialize(value: TransactionValue): Buffer {
+    const { transaction, blockHash, sequence, submittedSequence, timestamp } = value
+
+    const bw = bufio.write(this.getSize(value))
+    bw.writeVarBytes(transaction.serialize())
+    bw.writeU64(timestamp.getTime())
+
+    let flags = 0
+    flags |= Number(!!blockHash) << 0
+    flags |= Number(!!sequence) << 1
+    bw.writeU8(flags)
+
+    if (blockHash) {
+      bw.writeHash(blockHash)
+    }
+    if (sequence) {
+      bw.writeU32(sequence)
+    }
+
+    bw.writeU32(submittedSequence)
+
+    const assetCount = value.assetBalanceDeltas.size
+    bw.writeU32(assetCount)
+
+    for (const [assetId, balanceDelta] of value.assetBalanceDeltas) {
+      bw.writeHash(assetId)
+      bw.writeBigI64(balanceDelta)
+    }
+
+    return bw.render()
+  }
+
+  deserialize(buffer: Buffer): TransactionValue {
+    const reader = bufio.read(buffer, true)
+    const transaction = new Transaction(reader.readVarBytes())
+    const timestamp = new Date(reader.readU64())
+
+    const flags = reader.readU8()
+    const hasBlockHash = flags & (1 << 0)
+    const hasSequence = flags & (1 << 1)
+
+    let blockHash = null
+    if (hasBlockHash) {
+      blockHash = reader.readHash()
+    }
+
+    let sequence = null
+    if (hasSequence) {
+      sequence = reader.readU32()
+    }
+
+    const submittedSequence = reader.readU32()
+
+    const assetBalanceDeltas = new BufferMap<bigint>()
+    const assetCount = reader.readU32()
+
+    for (let i = 0; i < assetCount; i++) {
+      const assetId = reader.readHash()
+      const balanceDelta = reader.readBigI64()
+      assetBalanceDeltas.set(assetId, balanceDelta)
+    }
+
+    return {
+      transaction,
+      blockHash,
+      submittedSequence,
+      sequence,
+      timestamp,
+      assetBalanceDeltas,
+    }
+  }
+
+  getSize(value: TransactionValue): number {
+    let size = bufio.sizeVarBytes(value.transaction.serialize())
+    size += 8
+    size += 1
+    if (value.blockHash) {
+      size += 32
+    }
+    if (value.sequence) {
+      size += 4
+    }
+    size += 4
+    size += 4
+    size += value.assetBalanceDeltas.size * (ASSET_ID_LENGTH + 8)
+    return size
+  }
+}
```

### ironfish/src/migrations/data/025-backfill-wallet-nullifier-to-transaction-hash/stores.ts
```diff
@@ -0,0 +1,16 @@
+/* This Source Code Form is subject to the terms of the Mozilla Public
+ * License, v. 2.0. If a copy of the MPL was not distributed with this
+ * file, You can obtain one at https://mozilla.org/MPL/2.0/. */
+import { IDatabase } from '../../../storage'
+import { GetNewStores } from './new'
+import { GetOldStores } from './old'
+
+export function GetStores(db: IDatabase): {
+  old: ReturnType<typeof GetOldStores>
+  new: ReturnType<typeof GetNewStores>
+} {
+  const oldStores = GetOldStores(db)
+  const newStores = GetNewStores(db)
+
+  return { old: oldStores, new: newStores }
+}
```

### ironfish/src/migrations/data/index.ts
```diff
@@ -13,6 +13,7 @@ import { Migration021 } from './021-add-version-to-accounts'
 import { Migration022 } from './022-add-view-key-account'
 import { Migration023 } from './023-wallet-optional-spending-key'
 import { Migration024 } from './024-unspent-notes'
+import { Migration025 } from './025-backfill-wallet-nullifier-to-transaction-hash'
 
 export const MIGRATIONS = [
   Migration014,
@@ -26,4 +27,5 @@ export const MIGRATIONS = [
   Migration022,
   Migration023,
   Migration024,
+  Migration025,
 ]
```

### ironfish/src/wallet/__fixtures__/account.test.ts.fixture
```diff
@@ -2861,5 +2861,257 @@
       "type": "Buffer",
       "data": "base64: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"
     }
+  ],
+  "Accounts addPendingTransaction should save the transaction hash for a nullifier if it does not already exist": [
+    {
+      "version": 1,
+      "id": "cdefb2d2-a461-4aa6-bcd7-34536f47e163",
+      "name": "test",
+      "spendingKey": "73df150cdb8fe44dfe65e3fd78d0f32ce42c7598bff47316237b1a4197d8c7ed",
+      "viewKey": "c71e638031efa4e88babc3aba068ec02b9a9a8c2090611e7b328589271e2a0c694dad2d2f887fd1d67d8729780c3519a5371a9f544c89764ee7347deef6ae0cc",
+      "incomingViewKey": "650a5a02a58944e170777450cd70ae86734f37477adb42704217c2fd2fbe3707",
+      "outgoingViewKey": "915e5333dae53d861487b497204771f06df2dcab8c22395647f51f9780e39225",
+      "publicAddress": "83c4345cfbbd95b8d41669a176c6e440d592d5fc6f57c16d26468a283ccc68b3"
+    },
+    {
+      "header": {
+        "sequence": 2,
+        "previousBlockHash": "D179D8B74987D6617267D46F4958554BA0DF02D7E5E6117DB02D6FF38FD0F6DA",
+        "noteCommitment": {
+          "type": "Buffer",
+          "data": "base64:KLZrekHfs3c1CHMp7SHa39SkoCWoivyBzmbGJjOOnyc="
+        },
+        "transactionCommitment": {
+          "type": "Buffer",
+          "data": "base64:M21UZjjyJNYwoVfo9qK4dT63f/IAEdsj0Eu+qBBGqPI="
+        },
+        "target": "883423532389192164791648750371459257913741948437809479060803100646309888",
+        "randomness": "0",
+        "timestamp": 1677270092744,
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000",
+        "noteSize": 4,
+        "work": "0"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGzKiP////8AAAAAdVFLDs1P1ktC6EYSqfaeIR4ryuan+W2dlQlrBgjmbJqr0ynA3baDDSNiYTa7E3NBSPy5S4i/O7s/I9wCGdx+iKAiEqqFyHh7jcheWkc2/9CozLPvCONMjGEyrSKPq/IpmjDCnVea+0EMNhVxnH1G975MoO7fQtwCdlYZjt+36X4Kvl7N3FpWqodihwLdw2Zk4L76RZQIfMQVEMwdQjelAwJ4F6SrPdMQ2C1Jq7OgX5qNngBicurrloPOLc6VX59oZ16t4doRVZnSyPEJ7Oy0f/zp459iMbX75GI0IwKojuvH6dp1kg+N8NsN///9V0aXf4Jc1b+nEbQzhOIRe/Eco4asxfwJz7Fr2Z4BV89J07h52EUifv7LpIkbFmLdBmAk3DdfZKCT2KgsvYUn8pcgTGngJwU7szTdR3ZIOT/6u2fYsr3Rish2geHdHAW5ZvJLWqzLI1rSB41nUno/VadonI2uIfrOU3zJk2pMdvQnY3EOpWh68lfZKedesrUuPJiN9s5+mfyc46xad/LTVlQn1Zl1waLprQzI5RiXCZzJ1j+1v2voRsQ1irhfSZhuxBfE6JI4J3lsJfqJ24EZg7jVcXEz/FVELhU2Y5E2DCn5mYaWQRTVZx7nzElyb24gRmlzaCBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwVKD4kpv7WZsTui4dvaf8Mte3ZQv3NBJzOxNnGDuURcP3VCvqyc15Ooz5XDOX4XWClTluVkCzPRcxJdHNQI6LAg=="
+        }
+      ]
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    }
+  ],
+  "Accounts addPendingTransaction should not overwrite the transaction hash for a nullifier if it already exists": [
+    {
+      "version": 1,
+      "id": "f472bb05-4ff9-4b9f-816f-0b42216158a9",
+      "name": "accountA",
+      "spendingKey": "6d325e7daf5da5c797aad7361fe3ad246942d93b2ec89cd44eb2813d255a2ee5",
+      "viewKey": "14ec253cd07a5abae2516b89bc069843fa60689aba4c9ab23dc530f471373470c993cc12d474e1dd73ad947868aa89471d780139e86a9eee7103f468608ae555",
+      "incomingViewKey": "fe903a5931a0e25f73ef25ff99fec9af83a03cc57bf34bee3084120b77efe501",
+      "outgoingViewKey": "dd08251521e7814c304b94ce9c3695461d5c188fa92556239023e97f9d03b1c2",
+      "publicAddress": "6cdf2435d2ea4b9e60b51c235a40e11833bebc082ac14bfe8cb36a9ac66947b6"
+    },
+    {
+      "header": {
+        "sequence": 2,
+        "previousBlockHash": "D179D8B74987D6617267D46F4958554BA0DF02D7E5E6117DB02D6FF38FD0F6DA",
+        "noteCommitment": {
+          "type": "Buffer",
+          "data": "base64:ddjYrOqY8XmBjId1nlwha3eMT5Y4UEuRn/VMpXUv0Fs="
+        },
+        "transactionCommitment": {
+          "type": "Buffer",
+          "data": "base64:bcI6CrCQV54JUeTuNPmpjyv7gt75mjN4ZTZSsIu5Pfs="
+        },
+        "target": "883423532389192164791648750371459257913741948437809479060803100646309888",
+        "randomness": "0",
+        "timestamp": 1677270095862,
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000",
+        "noteSize": 4,
+        "work": "0"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGzKiP////8AAAAAvI4r92TcyVXuqiFZYYgcI6r3Q+12U5BLkcOny14+dEeL2Xzp3d6XmrxgR5y1kybR7VbmYaDCB7Lv0GlSXeyG2WNBF5hO9IQm098e6R1f3ReRp7caOpOdtUfAdU0fTpgJYFnEXh1JKToTmir0JykoMhkIwh6BxdlxSCIASDLBN8wIP+/vM0ynShraT4WSLr+JsUPLszg/jS9Xg4I+bOiyl7zymJSsEOKdHy7TEXQLmoCh6lcggditEE8XMMuZBYTC8Tb4UoqhKbiwEkaO84/wFnhVQQjHb++lzeo6uh5z2d0IiG2FjEmQ3keHOlSvcY9sfbXzca5B68lYF1aA5+/g8o846bJkO8VyTOhQHDrE1htgk9FnG1SoZejCS+Ramx1R94N05/zfdPT97NQdIloSUgVooPMTgK2J5zsD+M7MuObKEiqHifQQLg/qN0oAfQFESfFYJVqhee+6QskFxPORLROYzYjfAbOePpklUcvA/b84QAO8Za1YG6VzHX1Kxn2zByNR0ghkSCXUbh06GqUYgJwBH64r6HwKPUaXrTsQ2XVhcb2bsyXvLqDjgADIJMsR/vNgOHCU/sbR7GBT2ksTiI+qtZNRxH3eU7Yj5Ryug2J0XKuSGG0EKklyb24gRmlzaCBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwShxwSprYJ3NqMQA4t73pbFv5v6Eye0hRcbZ4x5rz0d82aU0gv9SyUf6/VF6ajpfXvA0wYSwcjhWKgsondGbsCg=="
+        }
+      ]
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    },
+    {
+      "type": "Buffer",
+      "data": "base64:AQEAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjp3FqN8/Z2g3Y3Tbm9c1kRT1AUS9APJo521iYfYeBRmO92Fif2CKSE+k33S+ElXjtGKfE/DeLsMywE0WN1tLu0OiaFKGsprVBkUghqL9ow2rTkNJqwQ8Nm9xUzdulMXuVoLjxO9FjmuyMArHqlZn+OKmaqVKuNuICbfU5bDWxkcF2by2nugGnzGywIQcQ+guC6enMXY+vx9lZ659z0hwaSv81WZeCM2Nn7s6rc8bWkqyZGC4wVS8XqYpF+YuA6Nz29T5TzyVOMiWUIBURTezrxdSraPjS5J45XWQuamWdzOC7GaJXaDYPlXMKVarf7Qyh30yAaSat6w1pIi+NZBSinXY2KzqmPF5gYyHdZ5cIWt3jE+WOFBLkZ/1TKV1L9BbBAAAAFD76xRxz/FoQDaQ2dhGaME/DktI2mRA/ztEap2BpQxu5ErKb5zCGjb2Tz0+0YwjyyrcxXPh5nCZgVWkLCWueYLHQD6BBmQ43UVbHWR5Yafni6Z6Q0Jj5mEOUqDMDY0jCrIMuxatWVwfDwJREKO7aHXn1fVoJo3dTIFeuvsl2vkRx4d5gB2bbkCvBEPVaUSs+LHPuDtnvonoELwLdC2jUAHXEtjfknC7TZEp6YxQ0Yta36SJxAtIjTgDarZox0naRhZjGv7cwLMvne9lzSBjft9d2yOfS5RHZqdlUWh5qMWXEjOc0En5mkryfcc6kCRttqsmuYXXG6HF+5IXOOFBRmq64jQ77h9c6tBd4EMtx2EOKf9glb8v3C7f2T0ugnTH5sLSqGTjqTLDySIiBZAcykfG81a7uMompQ4JB1fwgbuj73WcuXz0uqXRT27yGM51JfpsHfpHSX0l5EzKLcVdoGmgnFHFAcp4LpSPttNbtmMj4htbrFsC9YQKLw17B/ucUUparINE/z5JD4gP8dYjWK5JBVsAeRHLD/Aj9cYI7NH90jbEVHQJmDKUkjh/FwIiBhChtwJ0cgdt/jAzw6I4+/8nNtvsU3qLou/b0SDsHTRgh0ZrA8e2l6QhtNmACYW4a58/ciR0c6mMVGaeEfxhGH35wdE3QpbnmqZpTaSjtT9femKJlfgG5MBSXNuxFLHiJQaLOMWijReG8FsGJOf6xkXM4eKukAHGISgRZuKxYETAqO1zPyZ/daDRpDPeStg41hFgBKF024T2xrJf73JllIYX8XuvN5y2EyAaTT+sXVChHyOoGyRw/8irbfzg3O4f7J4XmY2oVtf5Mb1mdd/Q6H6N3oHc9eys0Wf14LLTfchhBA+3S3W3Sd63/4jfhxQy/ztF9J6EsM/bP9GQLAyE4jZhl6MuGckHvu7u1KhLYsRDnXfbjIxv1vYKz/9vTh3KdSI3D7Rjlk1sFeZaTlVNEirCgi0jiZC7OqNBbugH9KI1oyHArZUv7LiiI1TkOqFPXDRW+Zs+6UT77RVAwDmp8iBNZOy+HcAtTnI+YXvM0M32itRJuIILQoJyyiFBsJlJPNl44yPaticABT5G7o33njALM2Gz824iuvu0dTh53ofBcCsh8smysAimZn63HwiE6sPEBGLRBB45l9RKt0O3sguaNyjW272sW7Sk/S/++k3qTnYcdS1YGFoY19kpDVzve5SFB8EzRB947C25ZhWtMrL+7POggONGzDU79ZyWeTvuKb0kom3SnaEerbLMn2TrOKr1FWpLTHXbXcMrIy1P/M+xN5VoQzC4+sGiP5VdGMShd6PIhaHbRW+G4GgJejNwtsJtnNiF+XuTsTx97L6scJJZCLGJuY6zQZfuidsMb/eiHVjvhmFZkSBnhjMyoQkdpCWE5nSSeJA+BRHKa1rvNgUgGHQTNSYRPqmMjt+nlkrkAmCEQr8dMLWNxzzwQy43doZ8kOnyfto4Wt+Yos2NwaN44ozUaOk8WywjagNgSbj0vjuyAAMaGUBk5gB66wCXN/exuXO8ZZzc+UlbigSPzbsWVEpeavj2RlfTtZvDjReW68QdbLS4pPwiGkw0s1C7CA=="
+    }
+  ],
+  "Accounts connectTransaction should overwrite the transaction hash for a nullifier if connected on a block": [
+    {
+      "version": 1,
+      "id": "80708f1c-1af6-4dfe-ada5-e88d6724013e",
+      "name": "accountA",
+      "spendingKey": "4752bfdf743bd0448ba7c5a510e8aebc0adae3707294cd50d9fd28870873e1df",
+      "viewKey": "f1130e6ed8b53e0b045fd9e8ff49bbead4e286eef438beb33d39a76547fbc29a1f15e8eb2fecac9acbb026b94293f33994b85975622487a31fe614708660e0e9",
+      "incomingViewKey": "c72944d6c16974a4698ce54f87da0e5297e57ccc12a450a0abc3bb945d246b06",
+      "outgoingViewKey": "187cc453a0dab7410b75f453c238e81d6212b011c19d201672aadaece3ce15aa",
+      "publicAddress": "3ce198bfefa22642abefd5be9bef5ef75bab4b6333a5b13cc0e6e92ce8a5cbc9"
+    },
+    {
+      "header": {
+        "sequence": 2,
+        "previousBlockHash": "D179D8B74987D6617267D46F4958554BA0DF02D7E5E6117DB02D6FF38FD0F6DA",
+        "noteCommitment": {
+          "type": "Buffer",
+          "data": "base64:ZbH152ImprcnYhstGG7qG2/5HWtll3khcvmAGJnMjkc="
+        },
+        "transactionCommitment": {
+          "type": "Buffer",
+          "data": "base64:TiQGSBaH614ZDit8reZLadU4V59baYcQKbe5JtFKrzA="
+        },
+        "target": "883423532389192164791648750371459257913741948437809479060803100646309888",
+        "randomness": "0",
+        "timestamp": 1677270105654,
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000",
+        "noteSize": 4,
+        "work": "0"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGzKiP////8AAAAA0daVQMGWJ4UkpXnTCJwXhPVt0yygjEEkmioI68nnNN2O8KYAFAY2fTzewFbpAXJ8pb2i3P5dPRXEKQjALP3N+clpVVYp4lcjsqbLokpqC/OB+vxFPxrp0Q/jlLvqBTS9NCXZQxsLjBanfZ1WrA892d9Jn/kVIi3tDI9I8lFPITIX0m+yah/FjVUee//3aXQNf2e1bz5EmMMk8Un6GR3GnnSTZwMdGi5LmnFr1ztD7nCoVkkHHtqMbq/TD0MxS3HgBCsbY0oc0e7abT0bLGxlZ1je2gPYgCgXA+Y95d7JEe2hNRTMHhRrTFd7ddnT9kcLrcCrdenzyzLgO5sXUvRpJfnHgAdFzhwYDM7gY5INyCfKwhT8W1pLqz0NJHavVY0R1WbBBkLfvmdOZ3bzLynDDPItiBeFXI14BrMMB9oU/IjYo96fwmwPPta8nOeFhs2RgnnnrQH9xLrs5XB5269DsoRrKcziFZZ0Out0skHee7+PaXAdUdaPbXjAIxgXwfkFaMk0StySdNdJv78+uvvQU/2cmm3rR4koaBrfbMI41WGMvSbqdqtLlKDiRXIiRXVW+i2U/s3wK9ag/fBvM0YlzS7fJSzVeYZ1tBBWbpwKqtYSESREK1fr9klyb24gRmlzaCBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw5bTV7TvIty1ZtY8ALNvfiIdwYfl8EMVweLz+guiQ08z4d0kVJqAcDgNQ7+l65PNiJQ9vRiyahl7m2DBLyKfgDQ=="
+        }
+      ]
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    },
+    {
+      "header": {
+        "sequence": 3,
+        "previousBlockHash": "91FC372576ED05036C77D8FD94D1F04769254AA30467B26D43B43966D808F9FB",
+        "noteCommitment": {
+          "type": "Buffer",
+          "data": "base64:OGkLTZWdvXas0VwxDaeeB9WzZeA/mFa2iYsCmyR8vCw="
+        },
+        "transactionCommitment": {
+          "type": "Buffer",
+          "data": "base64:36Q/q6RwDTwZJS3CX5mu+r3HEBz8WFXC/6CnDW2Z7pk="
+        },
+        "target": "880842937844725196442695540779332307793253899902937591585455087694081134",
+        "randomness": "0",
+        "timestamp": 1677270109006,
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000",
+        "noteSize": 7,
+        "work": "0"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGzKiP////8AAAAA9WL5ro2UsWrCqkFfNHND2QHdiEhZoRc8ROMADU5+QA2MTK8QREYsZ1Xvv0LYYCjpw5ZY1Tl1HjNe6rFijd5+XzNAL98m7McP+xzejUMbryuqwpc2PNmicjOBIJfibG9UpVnT5qxsQGFrWQojY74gMC3IkRVzGRh2rxExC2ePuk8JKhEgOsX+GagTr1M9JfO8zInJzQGGFS7I7mzrdVBBw6pkrvPySFdA6qfPYZgC096xxCay5t9kIPFXRQ3vIhRpxjZfegAsuqvblgU4EMZZ4Au6BC3KJ3YGlmg+v0GD5CBdy4eHD9KD4VtwYspBeO/Ri4XZ8koIBAErnLN8m4diAWBvKPuzgZkGOokyBhZac8TbQdsI8Gp2aWsFf807qmQBpeTMWaA366uRx3claDqchRyMn7m+gk3/cdGtr++fzMrRa596nCSrPXo1Rb0Om6hvzS9c+gAa2ESAgWJ89p8iwaA45VC1hYDYV9yJoUDO+/Lvqj2LpkVbQAmfqySLwyTLodW9TPmX8xHypoxJ8822i3HqyR+lM2RKmSZTaL5jzGfWPX7Sn+t9MaTStYuxAjbnlSsMLDoPzTkesaEJtBt908gpwK+IO8kEhhyzBaEyll06sK70UEw09Ulyb24gRmlzaCBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwqWYKzTqpbZIhSnvc9VHIPO35BLfWT7mC6RMJNzx+m+IAfi1TZzbYTWokS8IgWNnfD+6oecgsQnkSgIpzf+T5DA=="
+        },
+        {
+          "type": "Buffer",
+          "data": "base64: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"
+        }
+      ]
+    }
+  ],
+  "Accounts expireTransaction removes the nullifier to transaction hash if we are expiring the matching hash": [
+    {
+      "version": 1,
+      "id": "dbef8f44-75b4-4049-995b-2eb93477a9c1",
+      "name": "test",
+      "spendingKey": "5e7a39b921ab0a6831b5d5a32bac0559b34420358a563d8fcc72f1318eb38410",
+      "viewKey": "64351c6a8e63ae1410b4983a3e887d90f9ac26245a3e2bbef80f385784f34343d2c297cbd66ee74e2fc4d820a6275104bc763f1e51ee99342aa17aa95a501000",
+      "incomingViewKey": "47aaecea4d7ee1abbf073e472f9e2cccd5eb9483af00d20fccc6ad80c25c9505",
+      "outgoingViewKey": "b7dc65d5e0b9dfa351ca8c1c1459ed10f2b68077619dd85bea2d305bf1da2cf3",
+      "publicAddress": "3d68318eb26c942e72a7cbbf27e5587e09e89062bfcdab893b5a308cdb1b508e"
+    },
+    {
+      "header": {
+        "sequence": 2,
+        "previousBlockHash": "D179D8B74987D6617267D46F4958554BA0DF02D7E5E6117DB02D6FF38FD0F6DA",
+        "noteCommitment": {
+          "type": "Buffer",
+          "data": "base64:Y557RcQypAyaBKURCP/JFdQ3Ldw1R1oS38zsKG3aslU="
+        },
+        "transactionCommitment": {
+          "type": "Buffer",
+          "data": "base64:fXNruns6iU8mD4h+AuFZxbPlmMhPhEFxSuBp+cJuIFM="
+        },
+        "target": "883423532389192164791648750371459257913741948437809479060803100646309888",
+        "randomness": "0",
+        "timestamp": 1677270118651,
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000",
+        "noteSize": 4,
+        "work": "0"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGzKiP////8AAAAAtQXRDw5qhhQYMaxDnpSn2nOj2fhWxhSSsmToOklwAl6Q9M+6yRgORK+TaoBr/+1FK+plXjaCRDYQAxpHnoOjaVJZ5+Sku1hhQiXNe0xuW3SBQJZEJy5nHhqlzjViI4Z1DNIC8YgyXQ3VOZAYQhbEuMEhEfWkbibOyVhSZckTKWAYyDo8HbafeTGA2ZYuvaXkRmigMCVJdqRZ5wGj5s0UcfSYLrNvG5PNMF8+KufTsgGQXaxS9JIddM6RXcJ6jAHHSi5y8Iz4rEHXP/PgOflYBptw3/nfXWeBZ8QOcUHBlXs0LGuKqTYTt6fVOL2aegJWa/BCAw9ISCooch3LqfNPhBGrHLtVRL/pJTQ42G3ZWd/KJcpO3B4Sf7hHH4hwq0kOUEV9KAYC0CVEmpiA4hyGtaudkAxZvCObPiX7uQJkCNOwvpVLgMDNCfwIJSVBhDLlxMRaamml/fdNUmIVeNqgs/bDYvwbW1eYe+iSuWakI9WyzeNdk/9ZHBAKKhZ5cusx7TUQogSbYb9PpmDFpIF3lDby2ZTnRlolrzBjlPmngWTaEnzkMBSH3g03pSDu6rXZXH2XV0NwV6SyMWqBoGuNBeEELcMQnsWSAWJxFDsc8Xjiw4U0iJJxb0lyb24gRmlzaCBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw458JYtBrZ82GwqY4Un7h/4IefcpFQIo+eI3CYq5Ba+6VJg4nPc0VJNP9SF+uR55r4PtLmxUpvOM7uYPDUpOgAw=="
+        }
+      ]
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    }
+  ],
+  "Accounts expireTransaction does not update the nullifier to transaction hash mapping if the hash does not match": [
+    {
+      "version": 1,
+      "id": "ff1d8103-f159-400e-a994-272581f554bd",
+      "name": "accountA",
+      "spendingKey": "12105c2da1223ca01b13ff6a53da3439b273318b7ce100ccd1c6fb7f6392df19",
+      "viewKey": "02e602c8b570dd65fd72eea98f6f6d146f2d0b51efe1ea3dd53a6bad330c4aadd90fa14a37a5672208d84293f2838b6cc411bf45b9b4370e71dd492722443b67",
+      "incomingViewKey": "a4a7f41bffdda8457fe89a497290c37a19f82426842094aa883257ab31714f02",
+      "outgoingViewKey": "a4ec5714bd02b9cce9b028e8838609fb01cb14edf0c77018b7a28d80d6857b72",
+      "publicAddress": "b41f988e538a1de6f62699378b91cacc95d6e6207828d16c3b01625bfeb504e2"
+    },
+    {
+      "header": {
+        "sequence": 2,
+        "previousBlockHash": "D179D8B74987D6617267D46F4958554BA0DF02D7E5E6117DB02D6FF38FD0F6DA",
+        "noteCommitment": {
+          "type": "Buffer",
+          "data": "base64:jMb0F/hMqwPYj6UIj+EEa4pbKGXb3SLZkB+hWOIRkzw="
+        },
+        "transactionCommitment": {
+          "type": "Buffer",
+          "data": "base64:fPANjceAPyjHQpHWAwf4PKX6N6wOgdWMPVbKpnweRK4="
+        },
+        "target": "883423532389192164791648750371459257913741948437809479060803100646309888",
+        "randomness": "0",
+        "timestamp": 1677270121629,
+        "graffiti": "0000000000000000000000000000000000000000000000000000000000000000",
+        "noteSize": 4,
+        "work": "0"
+      },
+      "transactions": [
+        {
+          "type": "Buffer",
+          "data": "base64:AQAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGzKiP////8AAAAAt+eda5gPfTXygj9muNTN6sOJYP2ZN/OnVh4dEXImt9GKM8mBARbJJcse+/YnL0lTE2D9khqjKQHKya0q2L4KxsG8TcywsQvXTeAb+w93BU2XFIFglS0MInNDmEgdjOPJqWra620fb2NCzXCItX63wGIutLBP0yFDzEEXGK9NsrwTwLQmsAfRXJfeUiX5PU1Ai1AsBc4FoOVpZfMbW0zmUbgLT3/EPHuPJCSfHJumLfuwZcFChjBnRjuIGQEhuompDG6X6rPoBdfpR29IYlHrBwwJDvODE7OmKJRDOUetgAAh69oCtGRDHLcCYNd/+6KXyGjh0M6FY9hXzGvj51nfRMjyvvOh4+k6H4BbTHHOWv4zzMiul07SE012we3+PC1fld8n4PXtelsKE4rn18w8EiqGkUMwnbqy8VncFUNOiqi2jZo09KTypvW7GWx8n668KLLbvA8ajwYOS2eUCmEmpYTURX11Yj/CDRcsx+Hz643je3B+hs1EZhq/m+Fx7KVLYemk2GwSXmKfjVU/9WQdTgwdELC8+BAILezXLQCwCeO47E3SD76zJdlEpJSkohmdq3DBF4V2CYADvw/wniK9dtZxJ5gDaxpjL+ioNeOv2UjpM9LUZzu1wElyb24gRmlzaCBub3RlIGVuY3J5cHRpb24gbWluZXIga2V5MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwoewiAyexTsCNJa6oyzbAI3I96SVsUGmPXtQUIjmzD+G+2l40wrLnhk01lQaTWnUUIzaBcS1sKFIefiVP7dW0CQ=="
+        }
+      ]
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    },
+    {
+      "type": "Buffer",
+      "data": "base64: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"
+    }
   ]
 }
\ No newline at end of file
```

### ironfish/src/wallet/account.test.ts
```diff
@@ -363,6 +363,52 @@ describe('Accounts', () => {
       expect(pendingHashEntry).toBeDefined()
     })
 
+    it('should save the transaction hash for a nullifier if it does not already exist', async () => {
+      const { node } = nodeTest
+
+      const account = await useAccountFixture(node.wallet)
+      const block = await useMinerBlockFixture(node.chain, undefined, account, node.wallet)
+      await node.chain.addBlock(block)
+      await node.wallet.updateHead()
+
+      // Add a pending transaction and check the nullifier
+      const transaction = await useTxFixture(node.wallet, account, account)
+      const nullifier = transaction.getSpend(0).nullifier
+      const transactionHash = await account['walletDb'].getTransactionHashFromNullifier(
+        account,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transaction.hash())
+    })
+
+    it('should not overwrite the transaction hash for a nullifier if it already exists', async () => {
+      const { node: nodeA } = await nodeTest.createSetup()
+      const { node: nodeB } = await nodeTest.createSetup()
+
+      const accountA = await useAccountFixture(nodeA.wallet, 'accountA')
+      const accountB = await nodeB.wallet.importAccount(accountA)
+
+      // Ensure both nodes for the same account have the same note
+      const block = await useMinerBlockFixture(nodeA.chain, undefined, accountA, nodeA.wallet)
+      await nodeA.chain.addBlock(block)
+      await nodeA.wallet.updateHead()
+      await nodeB.chain.addBlock(block)
+      await nodeB.wallet.updateHead()
+
+      // Spend the same note in both nodes
+      const transactionA = await useTxFixture(nodeA.wallet, accountA, accountA)
+      const transactionB = await useTxFixture(nodeB.wallet, accountB, accountB)
+
+      // Add the pending transaction from Node B but ensure we have the original hash
+      await nodeA.wallet.addPendingTransaction(transactionB)
+      const nullifier = transactionB.getSpend(0).nullifier
+      const transactionHash = await accountA['walletDb'].getTransactionHashFromNullifier(
+        accountA,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transactionA.hash())
+    })
+
     it('should remove spent notes from unspentNoteHashes', async () => {
       const { node } = nodeTest
 
@@ -767,6 +813,50 @@ describe('Accounts', () => {
       })
     })
 
+    it('should overwrite the transaction hash for a nullifier if connected on a block', async () => {
+      const { node: nodeA } = await nodeTest.createSetup()
+      const { node: nodeB } = await nodeTest.createSetup()
+
+      const accountA = await useAccountFixture(nodeA.wallet, 'accountA')
+      const accountB = await nodeB.wallet.importAccount(accountA)
+
+      // Ensure both nodes for the same account have the same note
+      const block1 = await useMinerBlockFixture(nodeA.chain, undefined, accountA, nodeA.wallet)
+      await nodeA.chain.addBlock(block1)
+      await nodeA.wallet.updateHead()
+      await nodeB.chain.addBlock(block1)
+      await nodeB.wallet.updateHead()
+
+      // Spend the same note in both nodes
+      const transactionA = await useTxFixture(nodeA.wallet, accountA, accountA)
+      const transactionB = await useTxFixture(nodeB.wallet, accountB, accountB)
+
+      // Verify the existing record has the Transaction A Hash
+      const nullifier = transactionA.getSpend(0).nullifier
+      let transactionHash = await accountA['walletDb'].getTransactionHashFromNullifier(
+        accountA,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transactionA.hash())
+
+      const block2 = await useMinerBlockFixture(
+        nodeB.chain,
+        undefined,
+        accountB,
+        nodeB.wallet,
+        [transactionB],
+      )
+      await nodeA.chain.addBlock(block2)
+      await nodeA.wallet.updateHead()
+
+      // Verify the transaction hash for the nullifier has been overwritten
+      transactionHash = await accountA['walletDb'].getTransactionHashFromNullifier(
+        accountA,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transactionB.hash())
+    })
+
     it('should add received notes to unspentNoteHashes', async () => {
       const { node } = nodeTest
 
@@ -1571,6 +1661,90 @@ describe('Accounts', () => {
   })
 
   describe('expireTransaction', () => {
+    it('removes the nullifier to transaction hash if we are expiring the matching hash', async () => {
+      const { node } = nodeTest
+
+      const account = await useAccountFixture(node.wallet)
+      const block = await useMinerBlockFixture(node.chain, undefined, account, node.wallet)
+      await node.chain.addBlock(block)
+      await node.wallet.updateHead()
+
+      // Add a pending transaction and check the nullifier
+      const transaction = await useTxFixture(node.wallet, account, account)
+      const nullifier = transaction.getSpend(0).nullifier
+      const transactionHash = await account['walletDb'].getTransactionHashFromNullifier(
+        account,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transaction.hash())
+
+      // Verify the note is spent before expiration
+      const noteHash = await account.getNoteHash(nullifier)
+      Assert.isNotUndefined(noteHash)
+      let decryptedNote = await account.getDecryptedNote(noteHash)
+      Assert.isNotUndefined(decryptedNote)
+      expect(decryptedNote.spent).toBe(true)
+
+      // Verify the mapping is gone after expiration
+      await account.expireTransaction(transaction)
+      expect(
+        await account['walletDb'].getTransactionHashFromNullifier(account, nullifier),
+      ).toBeUndefined()
+
+      // Verify the note is unspent after expiration
+      decryptedNote = await account.getDecryptedNote(noteHash)
+      Assert.isNotUndefined(decryptedNote)
+      expect(decryptedNote.spent).toBe(false)
+    })
+
+    it('does not update the nullifier to transaction hash mapping if the hash does not match', async () => {
+      const { node: nodeA } = await nodeTest.createSetup()
+      const { node: nodeB } = await nodeTest.createSetup()
+
+      const accountA = await useAccountFixture(nodeA.wallet, 'accountA')
+      const accountB = await nodeB.wallet.importAccount(accountA)
+
+      // Ensure both nodes for the same account have the same note
+      const block = await useMinerBlockFixture(nodeA.chain, undefined, accountA, nodeA.wallet)
+      await nodeA.chain.addBlock(block)
+      await nodeA.wallet.updateHead()
+      await nodeB.chain.addBlock(block)
+      await nodeB.wallet.updateHead()
+
+      // Spend the same note in both nodes
+      const transactionA = await useTxFixture(nodeA.wallet, accountA, accountA)
+      const transactionB = await useTxFixture(nodeB.wallet, accountB, accountB)
+
+      // Add the pending transaction from Node B but ensure we have the original hash
+      await nodeA.wallet.addPendingTransaction(transactionB)
+      const nullifier = transactionB.getSpend(0).nullifier
+      let transactionHash = await accountA['walletDb'].getTransactionHashFromNullifier(
+        accountA,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transactionA.hash())
+
+      // Verify the note is spent before expiration
+      const noteHash = await accountA.getNoteHash(nullifier)
+      Assert.isNotUndefined(noteHash)
+      let decryptedNote = await accountA.getDecryptedNote(noteHash)
+      Assert.isNotUndefined(decryptedNote)
+      expect(decryptedNote.spent).toBe(true)
+
+      // Expire Transaction B but ensure we still have the nullifier to transaction hash mapping
+      await accountA.expireTransaction(transactionB)
+      transactionHash = await accountA['walletDb'].getTransactionHashFromNullifier(
+        accountA,
+        nullifier,
+      )
+      expect(transactionHash).toEqual(transactionA.hash())
+
+      // Verify the note is still spent since we expired a different transaction
+      decryptedNote = await accountA.getDecryptedNote(noteHash)
+      Assert.isNotUndefined(decryptedNote)
+      expect(decryptedNote.spent).toBe(true)
+    })
+
     it('should add spent notes back into unspentNoteHashes', async () => {
       const { node } = nodeTest
 
```

### ironfish/src/wallet/account.ts
```diff
@@ -191,6 +191,13 @@ export class Account {
 
         const spentNote = { ...note, spent: true }
         await this.walletDb.saveDecryptedNote(this, spentNoteHash, spentNote, tx)
+        await this.walletDb.saveNullifierToTransactionHash(
+          this,
+          spend.nullifier,
+          transaction,
+          tx,
+        )
+
         await this.walletDb.deleteUnspentNoteHash(this, spentNoteHash, spentNote, tx)
       }
 
@@ -490,6 +497,21 @@ export class Account {
 
         const spentNote = { ...note, spent: true }
         await this.walletDb.saveDecryptedNote(this, spentNoteHash, spentNote, tx)
+
+        const existingTransactionHash = await this.walletDb.getTransactionHashFromNullifier(
+          this,
+          spend.nullifier,
+          tx,
+        )
+        if (!existingTransactionHash) {
+          await this.walletDb.saveNullifierToTransactionHash(
+            this,
+            spend.nullifier,
+            transaction,
+            tx,
+          )
+        }
+
         await this.walletDb.deleteUnspentNoteHash(this, spentNoteHash, spentNote, tx)
       }
 
@@ -714,16 +736,25 @@ export class Account {
             'nullifierToNote mappings must have a corresponding decryptedNote',
           )
 
-          await this.walletDb.saveDecryptedNote(
+          const existingTransactionHash = await this.walletDb.getTransactionHashFromNullifier(
             this,
-            noteHash,
-            {
-              ...decryptedNote,
-              spent: false,
-            },
+            spend.nullifier,
             tx,
           )
-          await this.walletDb.addUnspentNoteHash(this, noteHash, decryptedNote, tx)
+          // Remove the nullifier to transaction hash mapping and mark the note as unspent
+          if (existingTransactionHash && existingTransactionHash.equals(transaction.hash())) {
+            await this.walletDb.deleteNullifierToTransactionHash(this, spend.nullifier, tx)
+            await this.walletDb.saveDecryptedNote(
+              this,
+              noteHash,
+              {
+                ...decryptedNote,
+                spent: false,
+              },
+              tx,
+            )
+            await this.walletDb.addUnspentNoteHash(this, noteHash, decryptedNote, tx)
+          }
         }
       }
 
```

### ironfish/src/wallet/walletdb/walletdb.ts
```diff
@@ -9,7 +9,7 @@ import { FileSystem } from '../../fileSystems'
 import { GENESIS_BLOCK_PREVIOUS } from '../../primitives/block'
 import { NoteEncryptedHash } from '../../primitives/noteEncrypted'
 import { Nullifier } from '../../primitives/nullifier'
-import { TransactionHash } from '../../primitives/transaction'
+import { Transaction, TransactionHash } from '../../primitives/transaction'
 import {
   BigU64BEEncoding,
   BUFFER_ENCODING,
@@ -39,7 +39,7 @@ import { HeadValue, NullableHeadValueEncoding } from './headValue'
 import { AccountsDBMeta, MetaValue, MetaValueEncoding } from './metaValue'
 import { TransactionValue, TransactionValueEncoding } from './transactionValue'
 
-const VERSION_DATABASE_ACCOUNTS = 24
+const VERSION_DATABASE_ACCOUNTS = 25
 
 const getAccountsDBMetaDefaults = (): AccountsDBMeta => ({
   defaultAccountId: null,
@@ -118,6 +118,11 @@ export class WalletDB {
     value: AssetValue
   }>
 
+  nullifierToTransactionHash: IDatabaseStore<{
+    key: [Account['prefix'], Buffer]
+    value: TransactionHash
+  }>
+
   unspentNoteHashes: IDatabaseStore<{
     key: [Account['prefix'], [Buffer, [number, [bigint, Buffer]]]]
     value: null
@@ -236,6 +241,12 @@ export class WalletDB {
       valueEncoding: new AssetValueEncoding(),
     })
 
+    this.nullifierToTransactionHash = this.db.addStore({
+      name: 'nt',
+      keyEncoding: new PrefixEncoding(new BufferEncoding(), new BufferEncoding(), 4),
+      valueEncoding: new BufferEncoding(),
+    })
+
     this.unspentNoteHashes = this.db.addStore({
       name: 'un',
       keyEncoding: new PrefixEncoding(
@@ -1107,4 +1118,33 @@ export class WalletDB {
   ): Promise<void> {
     await this.assets.del([account.prefix, assetId], tx)
   }
+
+  async getTransactionHashFromNullifier(
+    account: Account,
+    nullifier: Buffer,
+    tx?: IDatabaseTransaction,
+  ): Promise<Buffer | undefined> {
+    return this.nullifierToTransactionHash.get([account.prefix, nullifier], tx)
+  }
+
+  async saveNullifierToTransactionHash(
+    account: Account,
+    nullifier: Buffer,
+    transaction: Transaction,
+    tx?: IDatabaseTransaction,
+  ): Promise<void> {
+    await this.nullifierToTransactionHash.put(
+      [account.prefix, nullifier],
+      transaction.hash(),
+      tx,
+    )
+  }
+
+  async deleteNullifierToTransactionHash(
+    account: Account,
+    nullifier: Buffer,
+    tx?: IDatabaseTransaction,
+  ): Promise<void> {
+    await this.nullifierToTransactionHash.del([account.prefix, nullifier], tx)
+  }
 }
```
