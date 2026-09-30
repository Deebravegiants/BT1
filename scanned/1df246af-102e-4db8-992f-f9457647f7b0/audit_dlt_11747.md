# [?] Merge branch 'master' into fix-liquid-frontend-crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-02-04
Source: https://github.com/mempool/mempool/commit/229e122daf1dcf2940c252d43fd1cdac88d9d6b5
Type: security-commit

## Details
Merge branch 'master' into fix-liquid-frontend-crash

## Patch
### backend/src/api/bitcoin/bitcoin-api.interface.ts
```diff
@@ -106,6 +106,7 @@ export namespace IBitcoinApi {
       address?: string;              //  (string) bitcoin address
       addresses?: string[];           //  (string) bitcoin addresses
       pegout_chain?: string;         //  (string) Elements peg-out chain
+      pegout_address?: string;       //  (string) Elements peg-out address
       pegout_addresses?: string[];   //  (string) Elements peg-out addresses
     };
   }
```

### backend/src/api/database-migration.ts
```diff
@@ -7,7 +7,7 @@ import cpfpRepository from '../repositories/CpfpRepository';
 import { RowDataPacket } from 'mysql2';
 
 class DatabaseMigration {
-  private static currentVersion = 67;
+  private static currentVersion = 68;
   private queryTimeout = 3600_000;
   private statisticsAddedIndexed = false;
   private uniqueLogs: string[] = [];
@@ -566,6 +566,20 @@ class DatabaseMigration {
       await this.$executeQuery('ALTER TABLE `blocks_templates` ADD INDEX `version` (`version`)');
       await this.updateToSchemaVersion(67);
     }
+    
+    if (databaseSchemaVersion < 68 && config.MEMPOOL.NETWORK === "liquid") {
+      await this.$executeQuery('TRUNCATE TABLE elements_pegs');
+      await this.$executeQuery('ALTER TABLE elements_pegs ADD PRIMARY KEY (txid, txindex);');
+      await this.$executeQuery(`UPDATE state SET number = 0 WHERE name = 'last_elements_block';`);
+      // Create the federation_addresses table and add the two Liquid Federation change addresses in
+      await this.$executeQuery(this.getCreateFederationAddressesTableQuery(), await this.$checkIfTableExists('federation_addresses'));
+      await this.$executeQuery(`INSERT INTO federation_addresses (bitcoinaddress) VALUES ('bc1qxvay4an52gcghxq5lavact7r6qe9l4laedsazz8fj2ee2cy47tlqff4aj4')`); // Federation change address
+      await this.$executeQuery(`INSERT INTO federation_addresses (bitcoinaddress) VALUES ('3EiAcrzq1cELXScc98KeCswGWZaPGceT1d')`); // Federation change address
+      // Create the federation_txos table that uses the federation_addresses table as a foreign key
+      await this.$executeQuery(this.getCreateFederationTxosTableQuery(), await this.$checkIfTableExists('federation_txos'));
+      await this.$executeQuery(`INSERT INTO state VALUES('last_bitcoin_block_audit', 0, NULL);`);
+      await this.updateToSchemaVersion(68);
+    }
   }
 
   /**
@@ -813,6 +827,32 @@ class DatabaseMigration {
     ) ENGINE=InnoDB DEFAULT CHARSET=utf8;`;
   }
 
+  private getCreateFederationAddressesTableQuery(): string {
+    return `CREATE TABLE IF NOT EXISTS federation_addresses (
+      bitcoinaddress varchar(100) NOT NULL,
+      PRIMARY KEY (bitcoinaddress)
+    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;`;
+  }
+
+  private getCreateFederationTxosTableQuery(): string {
+    return `CREATE TABLE IF NOT EXISTS federation_txos (
+      txid varchar(65) NOT NULL,
+      txindex int(11) NOT NULL,
+      bitcoinaddress varchar(100) NOT NULL,
+      amount bigint(20) unsigned NOT NULL,
+      blocknumber int(11) unsigned NOT NULL,
+      blocktime int(11) unsigned NOT NULL,
+      unspent tinyint(1) NOT NULL,
+      lastblockupdate int(11) unsigned NOT NULL,
+      lasttimeupdate int(11) unsigned NOT NULL,
+      pegtxid varchar(65) NOT NULL,
+      pegindex int(11) NOT NULL,
+      pegblocktime int(11) unsigned NOT NULL,
+      PRIMARY KEY (txid, txindex), 
+      FOREIGN KEY (bitcoinaddress) REFERENCES federation_addresses (bitcoinaddress)
+    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;`;
+  }
+
   private getCreatePoolsTableQuery(): string {
     return `CREATE TABLE IF NOT EXISTS pools (
       id int(11) NOT NULL AUTO_INCREMENT,
```

### backend/src/api/liquid/elements-parser.ts
```diff
@@ -5,8 +5,12 @@ import { Common } from '../common';
 import DB from '../../database';
 import logger from '../../logger';
 
+const federationChangeAddresses = ['bc1qxvay4an52gcghxq5lavact7r6qe9l4laedsazz8fj2ee2cy47tlqff4aj4', '3EiAcrzq1cELXScc98KeCswGWZaPGceT1d'];
+const auditBlockOffsetWithTip = 1; // Wait for 1 block confirmation before processing the block in the audit process to reduce the risk of reorgs
+
 class ElementsParser {
   private isRunning = false;
+  private isUtxosUpdatingRunning = false;
 
   constructor() { }
 
@@ -32,12 +36,6 @@ class ElementsParser {
     }
   }
 
-  public async $getPegDataByMonth(): Promise<any> {
-    const query = `SELECT SUM(amount) AS amount, DATE_FORMAT(FROM_UNIXTIME(datetime), '%Y-%m-01') AS date FROM elements_pegs GROUP BY DATE_FORMAT(FROM_UNIXTIME(datetime), '%Y%m')`;
-    const [rows] = await DB.query(query);
-    return rows;
-  }
-
   protected async $parseBlock(block: IBitcoinApi.Block) {
     for (const tx of block.tx) {
       await this.$parseInputs(tx, block);
@@ -55,37 +53,53 @@ class ElementsParser {
 
   protected async $parsePegIn(input: IBitcoinApi.Vin, vindex: number, txid: string, block: IBitcoinApi.Block) {
     const bitcoinTx: IBitcoinApi.Transaction = await bitcoinSecondClient.getRawTransaction(input.txid, true);
+    const bitcoinBlock: IBitcoinApi.Block = await bitcoinSecondClient.getBlock(bitcoinTx.blockhash);
     const prevout = bitcoinTx.vout[input.vout || 0];
     const outputAddress = prevout.scriptPubKey.address || (prevout.scriptPubKey.addresses && prevout.scriptPubKey.addresses[0]) || '';
     await this.$savePegToDatabase(block.height, block.time, prevout.value * 100000000, txid, vindex,
-      outputAddress, bitcoinTx.txid, prevout.n, 1);
+      outputAddress, bitcoinTx.txid, prevout.n, bitcoinBlock.height, bitcoinBlock.time, 1);
   }
 
   protected async $parseOutputs(tx: IBitcoinApi.Transaction, block: IBitcoinApi.Block) {
     for (const output of tx.vout) {
       if (output.scriptPubKey.pegout_chain) {
         await this.$savePegToDatabase(block.height, block.time, 0 - output.value * 100000000, tx.txid, output.n,
-          (output.scriptPubKey.pegout_addresses && output.scriptPubKey.pegout_addresses[0] || ''), '', 0, 0);
+          (output.scriptPubKey.pegout_address || ''), '', 0, 0, 0, 0);
       }
       if (!output.scriptPubKey.pegout_chain && output.scriptPubKey.type === 'nulldata'
         && output.value && output.value > 0 && output.asset && output.asset === Common.nativeAssetId) {
         await this.$savePegToDatabase(block.height, block.time, 0 - output.value * 100000000, tx.txid, output.n,
-          (output.scriptPubKey.pegout_addresses && output.scriptPubKey.pegout_addresses[0] || ''), '', 0, 1);
+          (output.scriptPubKey.pegout_address || ''), '', 0, 0, 0, 1);
       }
     }
   }
 
   protected async $savePegToDatabase(height: number, blockTime: number, amount: number, txid: string,
-    txindex: number, bitcoinaddress: string, bitcointxid: string, bitcoinindex: number, final_tx: number): Promise<void> {
-    const query = `INSERT INTO elements_pegs(
+    txindex: number, bitcoinaddress: string, bitcointxid: string, bitcoinindex: number, bitcoinblock: number, bitcoinBlockTime: number, final_tx: number): Promise<void> {
+    const query = `INSERT IGNORE INTO elements_pegs(
         block, datetime, amount, txid, txindex, bitcoinaddress, bitcointxid, bitcoinindex, final_tx
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`;
 
     const params: (string | number)[] = [
       height, blockTime, amount, txid, txindex, bitcoinaddress, bitcointxid, bitcoinindex, final_tx
     ];
     await DB.query(query, params);
-    logger.debug(`Saved L-BTC peg from block height #${height} with TXID ${txid}.`);
+    logger.debug(`Saved L-BTC peg from Liquid block height #${height} with TXID ${txid}.`);
+
+    if (amount > 0) { // Peg-in
+  
+      // Add the address to the federation addresses table
+      await DB.query(`INSERT IGNORE INTO federation_addresses (bitcoinaddress) VALUES (?)`, [bitcoinaddress]);
+
+      // Add the UTXO to the federation txos table
+      const query_utxos = `INSERT IGNORE INTO federation_txos (txid, txindex, bitcoinaddress, amount, blocknumber, blocktime, unspent, lastblockupdate, lasttimeupdate, pegtxid, pegindex, pegblocktime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;
+      const params_utxos: (string | number)[] = [bitcointxid, bitcoinindex, bitcoinaddress, amount, bitcoinblock, bitcoinBlockTime, 1, bitcoinblock - 1, 0, txid, txindex, blockTime];
+      await DB.query(query_utxos, params_utxos);
+      const [minBlockUpdate] = await DB.query(`SELECT MIN(lastblockupdate) AS lastblockupdate FROM federation_txos WHERE unspent = 1`)
+      await this.$saveLastBlockAuditToDatabase(minBlockUpdate[0]['lastblockupdate']);
+      logger.debug(`Saved new Federation UTXO ${bitcointxid}:${bitcoinindex} belonging to ${bitcoinaddress} to federation txos`);
+
+    }
   }
 
   protected async $getLatestBlockHeightFromDatabase(): Promise<number> {
@@ -98,6 +112,327 @@ class ElementsParser {
     const query = `UPDATE state SET number = ? WHERE name = 'last_elements_block'`;
     await DB.query(query, [blockHeight]);
   }
+
+  ///////////// FEDERATION AUDIT //////////////
+
+  public async $updateFederationUtxos() {
+    if (this.isUtxosUpdatingRunning) {
+      return;
+    }
+
+    this.isUtxosUpdatingRunning = true;
+
+    try {
+      let auditProgress = await this.$getAuditProgress();
+      // If no peg in transaction was found in the database, return
+      if (!auditProgress.lastBlockAudit) {
+        logger.debug(`No Federation UTXOs found in the database. Waiting for some to be confirmed before starting the Federation UTXOs audit`);
+        this.isUtxosUpdatingRunning = false;
+        return;
+      }
+
+      const bitcoinBlocksToSync = await this.$getBitcoinBlockchainState();
+      // If the bitcoin blockchain is not synced yet, return
+      if (bitcoinBlocksToSync.bitcoinHeaders > bitcoinBlocksToSync.bitcoinBlocks + 1) {
+        logger.debug(`Bitcoin client is not synced yet. ${bitcoinBlocksToSync.bitcoinHeaders - bitcoinBlocksToSync.bitcoinBlocks} blocks remaining to sync before the Federation audit process can start`);
+        this.isUtxosUpdatingRunning = false;
+        return;
+      }
+
+      auditProgress.lastBlockAudit++;
+
+      // Logging
+      let indexedThisRun = 0;
+      let timer = Date.now() / 1000;
+      const startedAt = Date.now() / 1000;
+      const indexingSpeeds: number[] = [];
+
+      while (auditProgress.lastBlockAudit <= auditProgress.confirmedTip) {
+
+        // First, get the current UTXOs that need to be scanned in the block
+        const utxos = await this.$getFederationUtxosToScan(auditProgress.lastBlockAudit);
+
+        // Get the peg-out addresses that need to be scanned
+        const redeemAddresses = await this.$getRedeemAddressesToScan();
+
+        // The fast way: check if these UTXOs are still unspent as of the current block with gettxout
+        let spentAsTip: any[];
+        let unspentAsTip: any[];
+        if (auditProgress.confirmedTip - auditProgress.lastBlockAudit <= 150) { // If the audit status is not too far in the past, we can use gettxout (fast way)
+          const utxosToParse = await this.$getFederationUtxosToParse(utxos);
+          spentAsTip = utxosToParse.spentAsTip;
+          unspentAsTip = utxosToParse.unspentAsTip;
+          logger.debug(`Found ${utxos.length} Federation UTXOs and ${redeemAddresses.length} Peg-Out Addresses to scan in Bitcoin block height #${auditProgress.lastBlockAudit} / #${auditProgress.confirmedTip}`);
+          logger.debug(`${unspentAsTip.length} / ${utxos.length} Federation UTXOs are unspent as of tip`);
+        } else { // If the audit status is too far in the past, it is useless and wasteful to look for still unspent txos since they will all be spent as of the tip
+          spentAsTip = utxos;
+          unspentAsTip = [];
+
+          // Logging
+          const elapsedSeconds = (Date.now() / 1000) - timer;
+          if (elapsedSeconds > 5) {
+            const runningFor = (Date.now() / 1000) - startedAt;
+            const blockPerSeconds = indexedThisRun / elapsedSeconds;
+            indexingSpeeds.push(blockPerSeconds);
+            if (indexingSpeeds.length > 100) indexingSpeeds.shift(); // Keep the length of the up to 100 last indexing speeds
+            const meanIndexingSpeed = indexingSpeeds.reduce((a, b) => a + b, 0) / indexingSpeeds.length;
+            const eta = (auditProgress.confirmedTip - auditProgress.lastBlockAudit) / meanIndexingSpeed;
+            logger.debug(`Scanning ${utxos.length} Federation UTXOs and ${redeemAddresses.length} Peg-Out Addresses at Bitcoin block height #${auditProgress.lastBlockAudit} / #${auditProgress.confirmedTip} | ~${meanIndexingSpeed.toFixed(2)} blocks/sec | elapsed: ${(runningFor / 60).toFixed(0)} minutes | ETA: ${(eta / 60).toFixed(0)} minutes`);
+            timer = Date.now() / 1000;
+            indexedThisRun = 0;
+          }
+        }
+
+        // The slow way: parse the block to look for the spending tx
+        const blockHash: IBitcoinApi.ChainTips = await bitcoinSecondClient.getBlockHash(auditProgress.lastBlockAudit);
+        const block: IBitcoinApi.Block = await bitcoinSecondClient.getBlock(blockHash, 2);
+        await this.$parseBitcoinBlock(block, spentAsTip, unspentAsTip, auditProgress.confirmedTip, redeemAddresses);
+
+        // Finally, update the lastblockupdate of the remaining UTXOs and save to the database
+        const [minBlockUpdate] = await DB.query(`SELECT MIN(lastblockupdate) AS lastblockupdate FROM federation_txos WHERE unspent = 1`)
+        await this.$saveLastBlockAuditToDatabase(minBlockUpdate[0]['lastblockupdate']);
+
+        auditProgress = await this.$getAuditProgress();
+        auditProgress.lastBlockAudit++;
+        indexedThisRun++;
+      }
+
+      this.isUtxosUpdatingRunning = false;
+    } catch (e) {
+      this.isUtxosUpdatingRunning = false;
+      throw new Error(e instanceof Error ? e.message : 'Error');
+    } 
+  }
+
+  // Get the UTXOs that need to be scanned in block height (UTXOs that were last updated in the block height - 1)
+  protected async $getFederationUtxosToScan(height: number) { 
+    const query = `SELECT txid, txindex, bitcoinaddress, amount FROM federation_txos WHERE lastblockupdate = ? AND unspent = 1`;
+    const [rows] = await DB.query(query, [height - 1]);
+    return rows as any[];
+  }
+
+  // Returns the UTXOs that are spent as of tip and need to be scanned
+  protected async $getFederationUtxosToParse(utxos: any[]): Promise<any> {
+    const spentAsTip: any[] = [];
+    const unspentAsTip: any[] = [];
+
+    for (const utxo of utxos) {
+      const result = await bitcoinSecondClient.getTxOut(utxo.txid, utxo.txindex, false);
+      result ? unspentAsTip.push(utxo) : spentAsTip.push(utxo);
+    }
+    
+    return {spentAsTip, unspentAsTip};
+  }
+
+  protected async $parseBitcoinBlock(block: IBitcoinApi.Block, spentAsTip: any[], unspentAsTip: any[], confirmedTip: number, redeemAddressesData: any[] = []) {
+    const redeemAddresses: string[] = redeemAddressesData.map(redeemAddress => redeemAddress.bitcoinaddress);
+    for (const tx of block.tx) {
+      let mightRedeemInThisTx = false; // If a Federation UTXO is spent in this block, we might find a peg-out address in the outputs...
+      // Check if the Federation UTXOs that was spent as of tip are spent in this block
+      for (const input of tx.vin) {
+        const txo = spentAsTip.find(txo => txo.txid === input.txid && txo.txindex === input.vout);
+        if (txo) {
+          mightRedeemInThisTx = true;
+          await DB.query(`UPDATE federation_txos SET unspent = 0, lastblockupdate = ?, lasttimeupdate = ? WHERE txid = ? AND txindex = ?`, [block.height, block.time, txo.txid, txo.txindex]);
+          // Remove the TXO from the utxo array
+          spentAsTip.splice(spentAsTip.indexOf(txo), 1);
+          logger.debug(`Federation UTXO ${txo.txid}:${txo.txindex} (${txo.amount} sats) was spent in block ${block.height}`);
+        }
+      }
+      // Check if an output is sent to a change address of the federation
+      for (const output of tx.vout) {
+        if (output.scriptPubKey.address && federationChangeAddresses.includes(output.scriptPubKey.address)) {
+          // Check that the UTXO was not already added in the DB by previous scans
+          const [rows_check] = await DB.query(`SELECT txid FROM federation_txos WHERE txid = ? AND txindex = ?`, [tx.txid, output.n]) as any[];
+          if (rows_check.length === 0) {
+            const query_utxos = `INSERT INTO federation_txos (txid, txindex, bitcoinaddress, amount, blocknumber, blocktime, unspent, lastblockupdate, lasttimeupdate, pegtxid, pegindex, pegblocktime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;
+            const params_utxos: (string | number)[] = [tx.txid, output.n, output.scriptPubKey.address, output.value * 100000000, block.height, block.time, 1, block.height, 0, '', 0, 0];
+            await DB.query(query_utxos, params_utxos);
+            // Add the UTXO to the utxo array
+            spentAsTip.push({
+              txid: tx.txid,
+              txindex: output.n,
+              bitcoinaddress: output.scriptPubKey.address,
+              amount: output.value * 100000000
+            });
+            logger.debug(`Added new Federation UTXO ${tx.txid}:${output.n} (${output.value * 100000000} sats), change address: ${output.scriptPubKey.address}`);
+          }
+        }
+        if (mightRedeemInThisTx && output.scriptPubKey.address && redeemAddresses.includes(output.scriptPubKey.address)) {
+          // Find the number of times output.scriptPubKey.address appears in redeemAddresses. There can be address reuse for peg-outs...
+          const matchingAddress: any[] = redeemAddressesData.filter(redeemAddress => redeemAddress.bitcoinaddress === output.scriptPubKey.address && -redeemAddress.amount === Math.round(output.value * 100000000));
+          if (matchingAddress.length > 0) {
+            if (matchingAddress.length > 1) {
+              // If there are more than one peg out address with the same amount, we can't know which one redeemed the UTXO: we take the oldest one
+              matchingAddress.sort((a, b) => a.datetime - b.datetime);
+              logger.debug(`Found redeem txid ${tx.txid}:${output.n} to peg-out address ${matchingAddress[0].bitcoinaddress}, amount ${matchingAddress[0].amount}, datetime ${matchingAddress[0].datetime}`);
+            } else {
+              logger.debug(`Found redeem txid ${tx.txid}:${output.n} to peg-out address ${matchingAddress[0].bitcoinaddress}, amount ${matchingAddress[0].amount}`);
+            }
+            const query_add_redeem = `UPDATE elements_pegs SET bitcointxid = ?, bitcoinindex = ? WHERE bitcoinaddress = ? AND amount = ? AND datetime = ?`;
+            const params_add_redeem: (string | number)[] = [tx.txid, output.n, matchingAddress[0].bitcoinaddress, matchingAddress[0].amount, matchingAddress[0].datetime];
+            await DB.query(query_add_redeem, params_add_redeem);
+            const index = redeemAddressesData.indexOf(matchingAddress[0]);
+            redeemAddressesData.splice(index, 1);
+            redeemAddresses.splice(index, 1);
+          } else { // The output amount does not match the peg-out amount... log it
+            logger.debug(`Found redeem txid ${tx.txid}:${output.n} to peg-out address ${output.scriptPubKey.address} but output amount ${Math.round(output.value * 100000000)} does not match the peg-out amount!`);
+          }
+        }
+      }
+    }
+
+
+    for (const utxo of spentAsTip) {
+      await DB.query(`UPDATE federation_txos SET lastblockupdate = ? WHERE txid = ? AND txindex = ?`, [block.height, utxo.txid, utxo.txindex]);    
+    }
+
+    for (const utxo of unspentAsTip) {
+      await DB.query(`UPDATE federation_txos SET lastblockupdate = ? WHERE txid = ? AND txindex = ?`, [confirmedTip, utxo.txid, utxo.txindex]);
+    }
+  }
+
+  protected async $saveLastBlockAuditToDatabase(blockHeight: number) {
+    const query = `UPDATE state SET number = ? WHERE name = 'last_bitcoin_block_audit'`;
+    await DB.query(query, [blockHeight]);
+  }
+
+  // Get the bitcoin block where the audit process was last updated
+  protected async $getAuditProgress(): Promise<any> {
+    const lastblockaudit = await this.$getLastBlockAudit();
+    const bitcoinBlocksToSync = await this.$getBitcoinBlockchainState();
+    return {
+      lastBlockAudit: lastblockaudit,
+      confirmedTip: bitcoinBlocksToSync.bitcoinBlocks - auditBlockOffsetWithTip,
+    };
+  }
+
+  // Get the bitcoin blocks remaining to be synced
+  protected async $getBitcoinBlockchainState(): Promise<any> {
+    const result = await bitcoinSecondClient.getBlockchainInfo();
+    return {
+      bitcoinBlocks: result.blocks,
+      bitcoinHeaders: result.headers,
+    }
+  }
+
+  protected async $getLastBlockAudit(): Promise<number> {
+    const query = `SELECT number FROM state WHERE name = 'last_bitcoin_block_audit'`;
+    const [rows] = await DB.query(query);
+    return rows[0]['number'];
+  }
+
+  protected async $getRedeemAddressesToScan(): Promise<any[]> {
+    const query = `SELECT datetime, amount, bitcoinaddress FROM elements_pegs where amount < 0 AND bitcoinaddress != '' AND bitcointxid = '';`;
+    const [rows]: any[] = await DB.query(query);
+    return rows;
+  }
+
+  ///////////// DATA QUERY //////////////
+
+  public async $getAuditStatus(): Promise<any> {
+    const lastBlockAudit = await this.$getLastBlockAudit();
+    const bitcoinBlocksToSync = await this.$getBitcoinBlockchainState();
+    return {
+      bitcoinBlocks: bitcoinBlocksToSync.bitcoinBlocks,
+      bitcoinHeaders: bitcoinBlocksToSync.bitcoinHeaders,
+      lastBlockAudit: lastBlockAudit,
+      isAuditSynced: bitcoinBlocksToSync.bitcoinHeaders - bitcoinBlocksToSync.bitcoinBlocks <= 2 && bitcoinBlocksToSync.bitcoinBlocks - lastBlockAudit <= 3,
+    };
+  }
+
+  public async $getPegDataByMonth(): Promise<any> {
+    const query = `SELECT SUM(amount) AS amount, DATE_FORMAT(FROM_UNIXTIME(datetime), '%Y-%m-01') AS date FROM elements_pegs GROUP BY DATE_FORMAT(FROM_UNIXTIME(datetime), '%Y%m')`;
+    const [rows] = await DB.query(query);
+    return rows;
+  }
+
+  public async $getFederationReservesByMonth(): Promise<any> {
+    const query = `
+    SELECT SUM(amount) AS amount, DATE_FORMAT(FROM_UNIXTIME(blocktime), '%Y-%m-01') AS date FROM federation_txos 
+    WHERE
+        (blocktime > UNIX_TIMESTAMP(LAST_DAY(FROM_UNIXTIME(blocktime) - INTERVAL 1 MONTH) + INTERVAL 1 DAY))
+      AND 
+        ((unspent = 1) OR (unspent = 0 AND lasttimeupdate > UNIX_TIMESTAMP(LAST_DAY(FROM_UNIXTIME(blocktime)) + INTERVAL 1 DAY)))
+    GROUP BY 
+        date;`;          
+    const [rows] = await DB.query(query);
+    return rows;
+  }
+
+  // Get the current L-BTC pegs and the last Liquid block it was updated
+  public async $getCurrentLbtcSupply(): Promise<any> {
+    const [rows] = await DB.query(`SELECT SUM(amount) AS LBTC_supply FROM elements_pegs;`);
+    const lastblockupdate = await this.$getLatestBlockHeightFromDatabase();
+    const hash = await bitcoinClient.getBlockHash(lastblockupdate);
+    return {
+      amount: rows[0]['LBTC_supply'],
+      lastBlockUpdate: lastblockupdate,
+      hash: hash
+    };
+  }
+
+  // Get the current reserves of the federation and the last Bitcoin block it was updated
+  public async $getCurrentFederationReserves(): Promise<any> {
+    const [rows] = await DB.query(`SELECT SUM(amount) AS total_balance FROM federation_txos WHERE unspent = 1;`);
+    const lastblockaudit = await this.$getLastBlockAudit();
+    const hash = await bitcoinSecondClient.getBlockHash(lastblockaudit);
+    return {
+      amount: rows[0]['total_balance'],
+      lastBlockUpdate: lastblockaudit,
+      hash: hash
+    };
+  }
+
+  // Get all of the federation addresses, most balances first
+  public async $getFederationAddresses(): Promise<any> {
+    const query = `SELECT bitcoinaddress, SUM(amount) AS balance FROM federation_txos WHERE unspent = 1 GROUP BY bitcoinaddress ORDER BY balance DESC;`;
+    const [rows] = await DB.query(query);
+    return rows;
+  }
+
+  // Get all of the UTXOs held by the federation, most recent first
+  public async $getFederationUtxos(): Promise<any> {
+    const query = `SELECT txid, txindex, bitcoinaddress, amount, blocknumber, blocktime, pegtxid, pegindex, pegblocktime FROM federation_txos WHERE unspent = 1 ORDER BY blocktime DESC;`;
+    const [rows] = await DB.query(query);
+    return rows;
+  }
+
+  // Get all of the federation addresses one month ago, most balances first
+  public async $getFederationAddressesOneMonthAgo(): Promise<any> {
+    const query = `
+    SELECT COUNT(*) AS addresses_count_one_month FROM (
+      SELECT bitcoinaddress, SUM(amount) AS balance
+      FROM federation_txos 
+      WHERE
+          (blocktime < UNIX_TIMESTAMP(TIMESTAMPADD(DAY, -30, CURRENT_TIMESTAMP())))
+        AND
+          ((unspent = 1) OR (unspent = 0 AND lasttimeupdate > UNIX_TIMESTAMP(TIMESTAMPADD(DAY, -30, CURRENT_TIMESTAMP()))))
+      GROUP BY bitcoinaddress
+    ) AS result;`;
+    const [rows] = await DB.query(query);
+    return rows[0];
+  }
+
+  // Get all of the UTXOs held by the federation one month ago, most recent first
+  public async $getFederationUtxosOneMonthAgo(): Promise<any> {
+    const query = `
+    SELECT COUNT(*) AS utxos_count_one_month FROM federation_txos 
+    WHERE
+        (blocktime < UNIX_TIMESTAMP(TIMESTAMPADD(DAY, -30, CURRENT_TIMESTAMP())))
+      AND
+        ((unspent = 1) OR (unspent = 0 AND lasttimeupdate > UNIX_TIMESTAMP(TIMESTAMPADD(DAY, -30, CURRENT_TIMESTAMP()))))
+    ORDER BY blocktime DESC;`;
+    const [rows] = await DB.query(query);
+    return rows[0];
+  }
+
+  // Get recent pegouts from the federation (3 months old)
+  public async $getRecentPegouts(): Promise<any> {
+    const query = `SELECT txid, txindex, amount, bitcoinaddress, bitcointxid, bitcoinindex, datetime AS blocktime FROM elements_pegs WHERE amount < 0 AND datetime > UNIX_TIMESTAMP(TIMESTAMPADD(DAY, -90, CURRENT_TIMESTAMP())) ORDER BY blocktime;`;
+    const [rows] = await DB.query(query);
+    return rows;
+  }
 }
 
 export default new ElementsParser();
```

### backend/src/api/liquid/liquid.routes.ts
```diff
@@ -15,7 +15,16 @@ class LiquidRoutes {
     
     if (config.DATABASE.ENABLED) {
       app
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/pegs', this.$getElementsPegs)
         .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/pegs/month', this.$getElementsPegsByMonth)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves', this.$getFederationReserves)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves/month', this.$getFederationReservesByMonth)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/pegouts', this.$getPegOuts)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves/addresses', this.$getFederationAddresses)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves/addresses/previous-month', this.$getFederationAddressesOneMonthAgo)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves/utxos', this.$getFederationUtxos)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves/utxos/previous-month', this.$getFederationUtxosOneMonthAgo)
+        .get(config.MEMPOOL.API_URL_PREFIX + 'liquid/reserves/status', this.$getFederationAuditStatus)
         ;
     }
   }
@@ -63,11 +72,123 @@ class LiquidRoutes {
   private async $getElementsPegsByMonth(req: Request, res: Response) {
     try {
       const pegs = await elementsParser.$getPegDataByMonth();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 60 * 60).toUTCString());
       res.json(pegs);
     } catch (e) {
       res.status(500).send(e instanceof Error ? e.message : e);
     }
   }
+
+  private async $getFederationReservesByMonth(req: Request, res: Response) {
+    try {
+      const reserves = await elementsParser.$getFederationReservesByMonth();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 60 * 60).toUTCString());
+      res.json(reserves);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getElementsPegs(req: Request, res: Response) {
+    try {
+      const currentSupply = await elementsParser.$getCurrentLbtcSupply();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 30).toUTCString());
+      res.json(currentSupply);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getFederationReserves(req: Request, res: Response) {
+    try {
+      const currentReserves = await elementsParser.$getCurrentFederationReserves();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 30).toUTCString());
+      res.json(currentReserves);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getFederationAuditStatus(req: Request, res: Response) {
+    try {
+      const auditStatus = await elementsParser.$getAuditStatus();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 30).toUTCString());
+      res.json(auditStatus);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getFederationAddresses(req: Request, res: Response) {
+    try {
+      const federationAddresses = await elementsParser.$getFederationAddresses();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 30).toUTCString());
+      res.json(federationAddresses);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getFederationAddressesOneMonthAgo(req: Request, res: Response) {
+    try {
+      const federationAddresses = await elementsParser.$getFederationAddressesOneMonthAgo();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 60 * 60 * 24).toUTCString());
+      res.json(federationAddresses);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getFederationUtxos(req: Request, res: Response) {
+    try {
+      const federationUtxos = await elementsParser.$getFederationUtxos();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 30).toUTCString());
+      res.json(federationUtxos);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getFederationUtxosOneMonthAgo(req: Request, res: Response) {
+    try {
+      const federationUtxos = await elementsParser.$getFederationUtxosOneMonthAgo();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 60 * 60 * 24).toUTCString());
+      res.json(federationUtxos);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
+  private async $getPegOuts(req: Request, res: Response) {
+    try {
+      const recentPegOuts = await elementsParser.$getRecentPegouts();
+      res.header('Pragma', 'public');
+      res.header('Cache-control', 'public');
+      res.setHeader('Expires', new Date(Date.now() + 1000 * 30).toUTCString());
+      res.json(recentPegOuts);
+    } catch (e) {
+      res.status(500).send(e instanceof Error ? e.message : e);
+    }
+  }
+
 }
 
 export default new LiquidRoutes();
```

### backend/src/index.ts
```diff
@@ -266,6 +266,7 @@ class Server {
       blocks.setNewBlockCallback(async () => {
         try {
           await elementsParser.$parse();
+          await elementsParser.$updateFederationUtxos();
         } catch (e) {
           logger.warn('Elements parsing error: ' + (e instanceof Error ? e.message : e));
         }
```

### contributors/natsoni.txt
```diff
@@ -1,3 +1,3 @@
 I hereby accept the terms of the Contributor License Agreement in the CONTRIBUTING.md file of the mempool/mempool git repository as of November 16, 2023.
 
-Signed: natsee
+Signed: natsoni
```

### frontend/src/app/components/amount/amount.component.html
```diff
@@ -19,7 +19,7 @@
   </ng-template>
   <ng-template #default>
     &lrm;{{ addPlus && satoshis >= 0 ? '+' : '' }}{{ satoshis / 100000000 | number : digitsInfo }}
-    <span class="symbol"><ng-template [ngIf]="network === 'liquid'">L-</ng-template>
+    <span class="symbol"><ng-template [ngIf]="network === 'liquid' && !forceBtc">L-</ng-template>
     <ng-template [ngIf]="network === 'liquidtestnet'">tL-</ng-template>
     <ng-template [ngIf]="network === 'testnet'">t</ng-template>
     <ng-template [ngIf]="network === 'signet'">s</ng-template>BTC</span>
```

### frontend/src/app/components/amount/amount.component.ts
```diff
@@ -23,6 +23,7 @@ export class AmountComponent implements OnInit, OnDestroy {
   @Input() noFiat = false;
   @Input() addPlus = false;
   @Input() blockConversion: Price;
+  @Input() forceBtc: boolean = false;
 
   constructor(
     private stateService: StateService,
```

### frontend/src/app/components/lbtc-pegs-graph/lbtc-pegs-graph.component.ts
```diff
@@ -27,7 +27,6 @@ export class LbtcPegsGraphComponent implements OnInit, OnChanges {
   template: ('widget' | 'advanced') = 'widget';
   isLoading = true;
 
-  pegsChartOption: EChartsOption = {};
   pegsChartInitOption = {
     renderer: 'svg'
   };
@@ -41,20 +40,24 @@ export class LbtcPegsGraphComponent implements OnInit, OnChanges {
   }
 
   ngOnChanges() {
-    if (!this.data) {
+    if (!this.data?.liquidPegs) {
       return;
     }
-    this.pegsChartOptions = this.createChartOptions(this.data.series, this.data.labels);
+    if (!this.data.liquidReserves) {
+      this.pegsChartOptions = this.createChartOptions(this.data.liquidPegs.series, this.data.liquidPegs.labels);
+    } else {
+      this.pegsChartOptions = this.createChartOptions(this.data.liquidPegs.series, this.data.liquidPegs.labels, this.data.liquidReserves.series);
+    }
   }
 
   rendered() {
-    if (!this.data) {
+    if (!this.data.liquidPegs) {
       return;
     }
     this.isLoading = false;
   }
 
-  createChartOptions(series: number[], labels: string[]): EChartsOption {
+  createChartOptions(pegSeries: number[], labels: string[], reservesSeries?: number[],): EChartsOption {
     return {
       grid: {
         height: this.height,
@@ -99,17 +102,18 @@ export class LbtcPegsGraphComponent implements OnInit, OnChanges {
           type: 'line',
         },
         formatter: (params: any) => {
-          const colorSpan = (color: string) => `<span class="indicator" style="background-color: #116761;"></span>`;
+          const colorSpan = (color: string) => `<span class="indicator" style="background-color: ${color};"></span>`;
           let itemFormatted = '<div class="title">' + params[0].axisValue + '</div>';
-          params.map((item: any, index: number) => {
+          for (let index = params.length - 1; index >= 0; index--) {
+            const item = params[index];
             if (index < 26) {
               itemFormatted += `<div class="item">
                 <div class="indicator-container">${colorSpan(item.color)}</div>
-                <div class="grow"></div>
-                <div class="value">${formatNumber(item.value, this.locale, '1.2-2')} <span class="symbol">L-BTC</span></div>
+                <div style="margin-right: 5px"></div>
+                <div class="value">${formatNumber(item.value, this.locale, '1.2-2')} <span class="symbol">${item.seriesName}</span></div>
               </div>`;
             }
-          });
+          }
           return `<div class="tx-wrapper-tooltip-chart ${(this.template === 'advanced') ? 'tx-wrapper-tooltip-chart-advanced' : ''}">${itemFormatted}</div>`;
         }
       },
@@ -138,20 +142,34 @@ export class LbtcPegsGraphComponent implements OnInit, OnChanges {
       },
       series: [
         {
-          data: series,
+          data: pegSeries,
+          name: 'L-BTC',
+          color: '#116761',
           type: 'line',
           stack: 'total',
-          smooth: false,
+          smooth: true,
           showSymbol: false,
           areaStyle: {
             opacity: 0.2,
             color: '#116761',
           },
           lineStyle: {
-            width: 3,
+            width: 2,
             color: '#116761',
           },
         },
+        {
+          data: reservesSeries,
+          name: 'BTC',
+          color: '#EA983B',
+          type: 'line',
+          smooth: true,
+          showSymbol: false,
+          lineStyle: {
+            width: 2,
+            color: '#EA983B',
+          },
+        },
       ],
     };
   }
```

### frontend/src/app/components/liquid-master-page/liquid-master-page.component.html
```diff
@@ -78,6 +78,9 @@ <h6 class="dropdown-header" i18n="master-page.layer2-networks-header">Layer 2 Ne
       <li class="nav-item" routerLinkActive="active" id="btn-assets">
         <a class="nav-link" [routerLink]="['/assets' | relativeUrl]" (click)="collapse()"><fa-icon [icon]="['fas', 'database']" [fixedWidth]="true" i18n-title="master-page.assets" title="Assets"></fa-icon></a>
       </li>
+      <li class="nav-item" routerLinkActive="active" [routerLinkActiveOptions]="{exact: true}" id="btn-audit">
+        <a class="nav-link" [routerLink]="['/audit']" (click)="collapse()"><fa-icon [icon]="['fas', 'scale-balanced']" [fixedWidth]="true" i18n-title="master-page.btc-reserves-audit" title="BTC Reserves Audit"></fa-icon></a>
+      </li>
       <li [hidden]="isMobile" class="nav-item mr-2" routerLinkActive="active" id="btn-docs">
         <a class="nav-link" [routerLink]="['/docs' | relativeUrl]" (click)="collapse()"><fa-icon [icon]="['fas', 'book']" [fixedWidth]="true" i18n-title="master-page.docs" title="Docs"></fa-icon></a>
       </li>
```

### frontend/src/app/components/liquid-reserves-audit/federation-addresses-list/federation-addresses-list.component.html
```diff
@@ -0,0 +1,72 @@
+<div [ngClass]="{'widget': widget}">
+
+  <div class="clearfix"></div>
+
+  <div style="min-height: 295px">
+    <table class="table table-borderless">
+      <thead style="vertical-align: middle;">
+        <th class="address text-left" [ngClass]="{'widget': widget}" i18n="shared.address">Address</th>
+        <th class="amount text-right" [ngClass]="{'widget': widget}" i18n="address.balance">Balance</th>
+      </thead>
+      <tbody *ngIf="federationAddresses$ | async as addresses; else skeleton" [style]="isLoading ? 'opacity: 0.75' : ''">
+        <ng-container *ngIf="widget; else regularRows">
+          <tr *ngFor="let address of addresses | slice:0:5">
+            <td class="address text-left widget">
+              <a href="{{ env.MEMPOOL_WEBSITE_URL + '/address/' + address.bitcoinaddress }}" target="_blank" style="color:#b86d12">
+                <app-truncate [text]="address.bitcoinaddress" [lastChars]="6"></app-truncate>
+              </a>
+            </td>
+            <td class="amount text-right widget">
+              <app-amount [satoshis]="+address.balance" [noFiat]="true" [forceBtc]="true"></app-amount>
+            </td>
+          </tr>
+        </ng-container>
+        <ng-template #regularRows>
+          <tr *ngFor="let address of addresses | slice:(page - 1) * pageSize:page * pageSize">
+            <td class="address text-left">
+              <a href="{{ env.MEMPOOL_WEBSITE_URL + '/address/' + address.bitcoinaddress }}" target="_blank" style="color:#b86d12">
+                <app-truncate [text]="address.bitcoinaddress" [lastChars]="6"></app-truncate>
+              </a>
+            </td>
+            <td class="amount text-right">
+              <app-amount [satoshis]="+address.balance" [noFiat]="true" [forceBtc]="true"></app-amount>
+            </td>
+          </tr>
+        </ng-template>
+      </tbody>
+      <ng-template #skeleton>
+        <tbody *ngIf="widget; else regularRowsSkeleton">
+          <tr *ngFor="let item of skeletonLines">
+            <td class="address text-left widget">
+              <span class="skeleton-loader" style="max-width: 400px"></span>
+            </td>
+            <td class="amount text-right widget">
+              <span class="skeleton-loader" style="max-width: 350px"></span>
+            </td>
+          </tr>
+        </tbody>
+        <ng-template #regularRowsSkeleton>
+          <tr *ngFor="let item of skeletonLines">
+            <td class="address text-left">
+              <span class="skeleton-loader" style="max-width: 600px"></span>
+            </td>
+            <td class="amount text-right">
+              <span class="skeleton-loader" style="max-width: 400px"></span>
+            </td>
+          </tr>
+        </ng-template>
+      </ng-template>
+    </table>
+
+    <ngb-pagination *ngIf="!widget && federationAddresses$ | async as addresses" class="pagination-container float-right mt-2" [class]="isLoading ? 'disabled' : ''"
+      [collectionSize]="addresses.length" [rotate]="true" [maxSize]="maxSize" [pageSize]="15" [(page)]="page"
+      (pageChange)="pageChange(page)" [boundaryLinks]="true" [ellipses]="false">
+    </ngb-pagination>
+
+    <ng-template [ngIf]="!widget">
+      <div class="clearfix"></div>
+      <br>
+    </ng-template>
+  </div>
+  
+</div>
```

### frontend/src/app/components/liquid-reserves-audit/federation-addresses-list/federation-addresses-list.component.scss
```diff
@@ -0,0 +1,45 @@
+.spinner-border {
+  height: 25px;
+  width: 25px;
+  margin-top: 13px;
+}
+
+tr, td, th {
+  border: 0px;
+  padding-top: 0.65rem !important;
+  padding-bottom: 0.6rem !important;
+  padding-right: 2rem !important;
+  .widget {
+    padding-right: 1rem !important;
+  }
+}
+
+.clear-link {
+  color: white;
+}
+
+.disabled {
+  pointer-events: none;
+  opacity: 0.5;
+}
+
+.progress {
+  background-color: #2d3348;
+}
+
+.address {
+  overflow: hidden;
+  text-overflow: ellipsis;
+  white-space: nowrap;
+  max-width: 160px;
+}
+.address.widget {
+  width: 60%;
+}
+
+.amount {
+  width: 25%;
+}
+.amount.widget {
+  width: 40%;
+}
```
