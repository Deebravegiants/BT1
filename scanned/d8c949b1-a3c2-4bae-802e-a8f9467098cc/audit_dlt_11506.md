# [?] Merge branch 'master' into fix-thead-overflow-mobile

## Summary
Severity: Unknown
Chain: Oracle
Component: bandprotocol/bandchain
Published: 2020-08-21
Source: https://github.com/bandprotocol/bandchain/commit/75a4be2e8b6626b4c7030acf9762575b30cfb918
Type: security-commit

## Details
Merge branch 'master' into fix-thead-overflow-mobile

## Patch
### CHANGELOG.md
```diff
@@ -8,6 +8,58 @@
 
 # Changelog
 
+## [v1.2.2](https://github.com/bandprotocol/bandchain/releases/tag/v1.2.2)
+
+### Chain (Non-consensus)
+
+- (feat) [\#2517](https://github.com/bandprotocol/bandchain/pull/2387) Switch to report only block if notice pending report for too long.
+- (impv) [\#2387](https://github.com/bandprotocol/bandchain/pull/2387) Implementation of allow free report transaction.
+
+### Yoda
+
+- (feat) [\#2484](https://github.com/bandprotocol/bandchain/pull/2484) yoda/runtime: Add verification environment variables
+
+### Emitter & Flusher
+
+- (impv) [\#2504](https://github.com/bandprotocol/bandchain/pull/2504) Change request-count-per-days from view to table
+- (bugs) [\#2505](https://github.com/bandprotocol/bandchain/pull/2505) fix bug related ds os table.
+- (feat) [\#2476](https://github.com/bandprotocol/bandchain/pull/2476) Implemented `historical_bonded_token_on_validators` table
+- (impv) [\#2495](https://github.com/bandprotocol/bandchain/pull/2495) Implemented `historical_oracle_statuses` table
+- (impv) [\#2452](https://github.com/bandprotocol/bandchain/pull/2452) Implemented view table to calculate oracle script response time
+- (impv) [\#2486](https://github.com/bandprotocol/bandchain/pull/2486) Implemented reporters table.
+- (impv) [\#2475](https://github.com/bandprotocol/bandchain/pull/2475) Add related data source and oracle script table.
+- (impv) [\#2450](https://github.com/bandprotocol/bandchain/pull/2450) Add request count 1day view table.
+
+### Scan
+
+- (impv) [\#2513](https://github.com/bandprotocol/bandchain/pull/2513) Implemented reporters table
+- (impv) [\#2511](https://github.com/bandprotocol/bandchain/pull/2511) Implemented report chart and oracle data reports tab
+- (impv) [\#2508](https://github.com/bandprotocol/bandchain/pull/2508) Implemented Your delegation info
+- (impv) [\#2503](https://github.com/bandprotocol/bandchain/pull/2503) Implemented Bonded Token Chart on Validator Index Page
+- (impv) [\#2501](https://github.com/bandprotocol/bandchain/pull/2501) Implemented Request Index Page
+- (impv) [\#2500](https://github.com/bandprotocol/bandchain/pull/2500) Implemented Delegators and ProposedBlock tabs
+- (impv) [\#2497](https://github.com/bandprotocol/bandchain/pull/2497) Implemented validator index top part and uptimechart
+- (impv) [\#2493](https://github.com/bandprotocol/bandchain/pull/2493) Implemented requests table for all requests page
+- (impv) [\#2492](https://github.com/bandprotocol/bandchain/pull/2492) Implemented OC index Top part, and patched padding bottom to section
+- (impv) [\#2491](https://github.com/bandprotocol/bandchain/pull/2491) Patched latest Txs and Blocks.
+- (impv) [\#2487](https://github.com/bandprotocol/bandchain/pull/2487) Updated OC requests tab on OC index page
+- (impv) [\#2485](https://github.com/bandprotocol/bandchain/pull/2485) Implemented make a request tab on OC index
+- (feat) [\#2482](https://github.com/bandprotocol/bandchain/pull/2482) Implemented latest requests.
+- (impv) [\#2481](https://github.com/bandprotocol/bandchain/pull/2481) Patched `ChainInfoHighlight` for revamp version.
+- (impv) [\#2478](https://github.com/bandprotocol/bandchain/pull/2478) Implemented New Header (aka TopBar), Navbar and Profile.
+- (impv) [\#2474](https://github.com/bandprotocol/bandchain/pull/2474) Implemented bride code tab for OC index page and added FontAwesome library with Icon component(it's from Peach)
+- (impv) [\#2473](https://github.com/bandprotocol/bandchain/pull/2473) Implemented OWASM code tab for OC index page, improved some components
+- (impv) [\#2471](https://github.com/bandprotocol/bandchain/pull/2471) Implemented the all oraclescripts page and refactor some part
+- (impv) [\#2456](https://github.com/bandprotocol/bandchain/pull/2456) Changed exit_code and external_id from int to string
+
+### Oracle Binary Encoding (OBI)
+
+- (impv) [\#2410](https://github.com/bandprotocol/bandchain/pull/2410) Improve code structure, Add PyObiBool and add more tests
+
+### Helpers
+
+- (feat) [\#2498](https://github.com/bandprotocol/bandchain/pull/2498) Implement wallet module
+
 ## [v1.2.1](https://github.com/bandprotocol/bandchain/releases/tag/v1.2.1)
 
 ### Chain (Non-consensus)
```

### CHANGELOG_UNRELEASED.md
```diff
@@ -12,44 +12,13 @@
 
 ### Chain (Non-consensus)
 
-- (impv) [\#2387](https://github.com/bandprotocol/bandchain/pull/2387) Implementation of allow free report transaction.
-
 ### Yoda
 
-- (feat) [\#2484](https://github.com/bandprotocol/bandchain/pull/2484) yoda/runtime: Add verification environment variables
-
 ### Emitter & Flusher
 
-- (bugs) [\#2505](https://github.com/bandprotocol/bandchain/pull/2505) fix bug related ds os table.
-- (feat) [\#2476](https://github.com/bandprotocol/bandchain/pull/2476) Implemented `historical_bonded_token_on_validators` table
-- (impv) [\#2495](https://github.com/bandprotocol/bandchain/pull/2495) Implemented `historical_oracle_statuses` table
-- (impv) [\#2452](https://github.com/bandprotocol/bandchain/pull/2452) Implemented view table to calculate oracle script response time
-- (impv) [\#2486](https://github.com/bandprotocol/bandchain/pull/2486) Implemented reporters table.
-- (impv) [\#2475](https://github.com/bandprotocol/bandchain/pull/2475) Add related data source and oracle script table.
-- (impv) [\#2450](https://github.com/bandprotocol/bandchain/pull/2450) Add request count 1day view table.
-
 ### Scan
 
 - (impv) [\#2516](https://github.com/bandprotocol/bandchain/pull/2516) Fix loading width and bg color
-- (impv) [\#2513](https://github.com/bandprotocol/bandchain/pull/2513) Implemented reporters table
-- (impv) [\#2511](https://github.com/bandprotocol/bandchain/pull/2511) Implemented report chart and oracle data reports tab
-- (impv) [\#2508](https://github.com/bandprotocol/bandchain/pull/2508) Implemented Your delegation info
-- (impv) [\#2503](https://github.com/bandprotocol/bandchain/pull/2503) Implemented Bonded Token Chart on Validator Index Page
-- (impv) [\#2501](https://github.com/bandprotocol/bandchain/pull/2501) Implemented Request Index Page
-- (impv) [\#2500](https://github.com/bandprotocol/bandchain/pull/2500) Implemented Delegators and ProposedBlock tabs
-- (impv) [\#2497](https://github.com/bandprotocol/bandchain/pull/2497) Implemented validator index top part and uptimechart
-- (impv) [\#2493](https://github.com/bandprotocol/bandchain/pull/2493) Implemented requests table for all requests page
-- (impv) [\#2492](https://github.com/bandprotocol/bandchain/pull/2492) Implemented OC index Top part, and patched padding bottom to section
-- (impv) [\#2491](https://github.com/bandprotocol/bandchain/pull/2491) Patched latest Txs and Blocks.
-- (impv) [\#2487](https://github.com/bandprotocol/bandchain/pull/2487) Updated OC requests tab on OC index page
-- (impv) [\#2485](https://github.com/bandprotocol/bandchain/pull/2485) Implemented make a request tab on OC index
-- (feat) [\#2482](https://github.com/bandprotocol/bandchain/pull/2482) Implemented latest requests.
-- (impv) [\#2481](https://github.com/bandprotocol/bandchain/pull/2481) Patched `ChainInfoHighlight` for revamp version.
-- (impv) [\#2478](https://github.com/bandprotocol/bandchain/pull/2478) Implemented New Header (aka TopBar), Navbar and Profile.
-- (impv) [\#2474](https://github.com/bandprotocol/bandchain/pull/2474) Implemented bride code tab for OC index page and added FontAwesome library with Icon component(it's from Peach)
-- (impv) [\#2473](https://github.com/bandprotocol/bandchain/pull/2473) Implemented OWASM code tab for OC index page, improved some components
-- (impv) [\#2471](https://github.com/bandprotocol/bandchain/pull/2471) Implemented the all oraclescripts page and refactor some part
-- (impv) [\#2456](https://github.com/bandprotocol/bandchain/pull/2456) Changed exit_code and external_id from int to string
 
 ### Bridges
 
@@ -59,10 +28,6 @@
 
 ### Oracle Binary Encoding (OBI)
 
-- (impv) [\#2410](https://github.com/bandprotocol/bandchain/pull/2410) Improve code structure, Add PyObiBool and add more tests
-
 ### Helpers
 
-- (feat) [\#2498](https://github.com/bandprotocol/bandchain/pull/2498) Implement wallet module
-
 ### MISC
```

### chain/emitter/app.go
```diff
@@ -161,7 +161,7 @@ func (app *App) InitChain(req abci.RequestInitChain) abci.ResponseInitChain {
 		app.emitSetDataSource(types.DataSourceID(idx+1), ds, nil)
 	}
 	for idx, os := range oracleState.OracleScripts {
-		app.emitSetOracleScript(types.OracleScriptID(idx+1), os, nil)
+		app.emitNewOracleScript(types.OracleScriptID(idx+1), os, nil)
 	}
 	app.FlushMessages()
 	return res
```

### chain/emitter/oracle.go
```diff
@@ -25,6 +25,19 @@ func (app *App) emitSetDataSource(id types.DataSourceID, ds types.DataSource, tx
 	})
 }
 
+func (app *App) emitNewOracleScript(id types.OracleScriptID, os types.OracleScript, txHash []byte) {
+	app.Write("NEW_ORACLE_SCRIPT", JsDict{
+		"id":              id,
+		"name":            os.Name,
+		"description":     os.Description,
+		"owner":           os.Owner.String(),
+		"schema":          os.Schema,
+		"codehash":        os.Filename,
+		"source_code_url": os.SourceCodeURL,
+		"tx_hash":         txHash,
+	})
+}
+
 func (app *App) emitSetOracleScript(id types.OracleScriptID, os types.OracleScript, txHash []byte) {
 	app.Write("SET_ORACLE_SCRIPT", JsDict{
 		"id":              id,
@@ -63,6 +76,7 @@ func (app *App) handleMsgRequestData(
 		"sender":           msg.Sender.String(),
 		"client_id":        msg.ClientID,
 		"resolve_status":   types.ResolveStatus_Open,
+		"timestamp":        app.DeliverContext.BlockTime().UnixNano(),
 	})
 	for _, raw := range req.RawRequests {
 		app.Write("NEW_RAW_REQUEST", JsDict{
@@ -121,7 +135,7 @@ func (app *App) handleMsgCreateOracleScript(
 ) {
 	id := types.OracleScriptID(atoi(evMap[types.EventTypeCreateOracleScript+"."+types.AttributeKeyID][0]))
 	os := app.BandApp.OracleKeeper.MustGetOracleScript(app.DeliverContext, id)
-	app.emitSetOracleScript(id, os, txHash)
+	app.emitNewOracleScript(id, os, txHash)
 	extra["id"] = id
 }
 
```

### chain/go.mod
```diff
@@ -12,6 +12,7 @@ require (
 	github.com/golang/protobuf v1.4.2
 	github.com/google/shlex v0.0.0-20191202100458-e7afc7fbc510
 	github.com/gorilla/mux v1.7.4
+	github.com/hashicorp/golang-lru v0.5.4
 	github.com/kyokomi/emoji v2.2.4+incompatible
 	github.com/levigross/grequests v0.0.0-20190908174114-253788527a1a
 	github.com/oasisprotocol/oasis-core/go v0.0.0-20200730171716-3be2b460b3ac
```

### chain/x/oracle/ante/ante.go
```diff
@@ -1,17 +1,30 @@
 package ante
 
 import (
+	"fmt"
+
 	sdk "github.com/cosmos/cosmos-sdk/types"
+	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
+	lru "github.com/hashicorp/golang-lru"
 
 	"github.com/bandprotocol/bandchain/chain/x/oracle"
 	"github.com/bandprotocol/bandchain/chain/x/oracle/keeper"
 )
 
-func checkValidReportMsg(ctx sdk.Context, oracleKeeper oracle.Keeper, msg sdk.Msg) bool {
-	rep, ok := msg.(oracle.MsgReportData)
-	if !ok {
-		return false
+var (
+	repTxCount       *lru.Cache
+	nextRepOnlyBlock int64
+)
+
+func init() {
+	var err error
+	repTxCount, err = lru.New(20000)
+	if err != nil {
+		panic(err)
 	}
+}
+
+func checkValidReportMsg(ctx sdk.Context, oracleKeeper oracle.Keeper, rep oracle.MsgReportData) bool {
 	if !oracleKeeper.IsReporter(ctx, rep.Validator, rep.Reporter) {
 		return false
 	}
@@ -37,17 +50,35 @@ func checkValidReportMsg(ctx sdk.Context, oracleKeeper oracle.Keeper, msg sdk.Ms
 	return true
 }
 
-// NewFeelessReportsAnteHandler returns a new ante handler that waives minimum gas price requirement
-// if the incoming tx is a valid report transaction.
+// NewFeelessReportsAnteHandler returns a new ante handler that waives minimum gas price
+// requirement if the incoming tx is a valid report transaction.
 func NewFeelessReportsAnteHandler(ante sdk.AnteHandler, oracleKeeper oracle.Keeper) sdk.AnteHandler {
 	return func(ctx sdk.Context, tx sdk.Tx, simulate bool) (newCtx sdk.Context, err error) {
 		if ctx.IsCheckTx() && !simulate {
+			// TODO: Move this out of "FeelessReports" ante handler.
+			isRepOnlyBlock := ctx.BlockHeight() == nextRepOnlyBlock
 			isValidReportTx := true
 			for _, msg := range tx.GetMsgs() {
-				if !checkValidReportMsg(ctx, oracleKeeper, msg) {
+				rep, ok := msg.(oracle.MsgReportData)
+				if !ok || !checkValidReportMsg(ctx, oracleKeeper, rep) {
 					isValidReportTx = false
 					break
 				}
+				if !isRepOnlyBlock {
+					key := fmt.Sprintf("%s:%d", rep.Validator.String(), rep.RequestID)
+					val, ok := repTxCount.Get(key)
+					nextVal := 1
+					if ok {
+						nextVal = val.(int) + 1
+					}
+					repTxCount.Add(key, nextVal)
+					if nextVal > 20 {
+						nextRepOnlyBlock = ctx.BlockHeight() + 1
+					}
+				}
+			}
+			if isRepOnlyBlock && !isValidReportTx {
+				return ctx, sdkerrors.Wrap(sdkerrors.ErrInvalidRequest, "Block reserved for report txs")
 			}
 			if isValidReportTx {
 				minGas := ctx.MinGasPrices()
```

### flusher/flusher/db.py
```diff
@@ -1,5 +1,5 @@
 import base64 as b64
-from datetime import datetime
+from datetime import datetime, date
 import sqlalchemy as sa
 import enum
 
@@ -73,6 +73,16 @@ def process_bind_param(self, value, dialect):
         return b64.decodestring(value.encode())
 
 
+class CustomDate(sa.types.TypeDecorator):
+    """Custom Date type that accepts Python nanosecond epoch int."""
+
+    impl = sa.Date
+
+    def process_bind_param(self, value, dialect):
+        dt = datetime.fromtimestamp(value / 1e9)
+        return date(dt.year, dt.month, dt.day)
+
+
 def Column(*args, **kwargs):
     """Forward into SQLAlchemy's Column construct, but with 'nullable' default to False."""
     if "nullable" not in kwargs:
@@ -327,6 +337,7 @@ def Column(*args, **kwargs):
     Column("bonded_tokens", sa.DECIMAL),
     Column("timestamp", CustomDateTime, primary_key=True),
 )
+
 reporters = sa.Table(
     "reporters",
     metadata,
@@ -348,3 +359,17 @@ def Column(*args, **kwargs):
     Column("status", sa.Boolean),
     Column("timestamp", CustomDateTime, primary_key=True),
 )
+
+oracle_script_requests = sa.Table(
+    "oracle_script_requests",
+    metadata,
+    Column("oracle_script_id", sa.Integer, sa.ForeignKey("oracle_scripts.id"), primary_key=True),
+    Column("count", sa.Integer),
+)
+
+request_count_per_days = sa.Table(
+    "request_count_per_days",
+    metadata,
+    Column("date", CustomDate, primary_key=True),
+    Column("count", sa.Integer),
+)
```

### flusher/flusher/handler.py
```diff
@@ -27,6 +27,8 @@
     reporters,
     related_data_source_oracle_scripts,
     historical_oracle_statuses,
+    oracle_script_requests,
+    request_count_per_days,
 )
 
 
@@ -49,6 +51,11 @@ def get_account_id(self, address):
             select([accounts.c.id]).where(accounts.c.address == address)
         ).scalar()
 
+    def get_request_count(self, date):
+        return self.conn.execute(
+            select([request_count_per_days.c.count]).where(request_count_per_days.c.date == date)
+        ).scalar()
+
     def handle_new_block(self, msg):
         self.conn.execute(blocks.insert(), msg)
 
@@ -84,6 +91,10 @@ def handle_set_data_source(self, msg):
             .on_conflict_do_update(constraint="data_sources_pkey", set_=msg)
         )
 
+    def handle_new_oracle_script(self, msg):
+        self.handle_set_oracle_script(msg)
+        self.handle_new_oracle_script_request({"oracle_script_id": msg["id"], "count": 0})
+
     def handle_set_oracle_script(self, msg):
         if msg["tx_hash"] is not None:
             msg["transaction_id"] = self.get_transaction_id(msg["tx_hash"])
@@ -99,7 +110,10 @@ def handle_set_oracle_script(self, msg):
     def handle_new_request(self, msg):
         msg["transaction_id"] = self.get_transaction_id(msg["tx_hash"])
         del msg["tx_hash"]
+        self.handle_set_request_count_per_days({"date": msg["timestamp"]})
+        del msg["timestamp"]
         self.conn.execute(requests.insert(), msg)
+        self.handle_set_oracle_script_request({"oracle_script_id": msg["oracle_script_id"]})
 
     def handle_update_request(self, msg):
         condition = True
@@ -294,3 +308,30 @@ def handle_set_historical_validator_status(self, msg):
             .values(**msg)
             .on_conflict_do_update(constraint="historical_oracle_statuses_pkey", set_=msg)
         )
+
+    def handle_new_oracle_script_request(self, msg):
+        self.conn.execute(oracle_script_requests.insert(), msg)
+
+    def handle_set_oracle_script_request(self, msg):
+        condition = True
+        for col in oracle_script_requests.primary_key.columns.values():
+            condition = (col == msg[col.name]) & condition
+        self.conn.execute(
+            oracle_script_requests.update(condition).values(
+                count=oracle_script_requests.c.count + 1
+            )
+        )
+
+    def handle_set_request_count_per_days(self, msg):
+        if self.get_request_count(msg["date"]) is None:
+            msg["count"] = 1
+            self.conn.execute(request_count_per_days.insert(), msg)
+        else:
+            condition = True
+            for col in request_count_per_days.primary_key.columns.values():
+                condition = (col == msg[col.name]) & condition
+            self.conn.execute(
+                request_count_per_days.update(condition).values(
+                    count=request_count_per_days.c.count + 1
+                )
+            )
```

### flusher/flusher/init.py
```diff
@@ -55,15 +55,6 @@ def init(chain_id, topic, db):
 			WHERE block_height > (SELECT MAX(height) from blocks) - 10000
 			GROUP BY consensus_address, voted;"""
     )
-    engine.execute(
-        """CREATE VIEW request_count_1day AS
-            SELECT date_trunc('day', blocks.timestamp) as date, COUNT(*) as request_count
-            FROM blocks
-            JOIN transactions ON blocks.height = transactions.block_height
-            JOIN requests ON requests.transaction_id = transactions.id
-            GROUP BY date;
-            """
-    )
     engine.execute(
         """CREATE VIEW oracle_script_statistic_last_1_day AS
             SELECT
@@ -77,7 +68,6 @@ def init(chain_id, topic, db):
             GROUP BY oracle_scripts.id, requests.resolve_status;
         """
     )
-
     engine.execute(
         """CREATE VIEW oracle_script_statistic_last_1_week AS
             SELECT
@@ -91,7 +81,6 @@ def init(chain_id, topic, db):
             GROUP BY oracle_scripts.id, requests.resolve_status;
         """
     )
-
     engine.execute(
         """CREATE VIEW oracle_script_statistic_last_1_month AS
             SELECT
```

### scan/src/components/ChainInfoHighlights.re
```diff
@@ -16,7 +16,7 @@ module Styles = {
       zIndex(2),
       height(`px(130)),
       padding2(~v=`px(16), ~h=`px(24)),
-      Media.mobile([padding2(~v=`px(16), ~h=`px(12))]),
+      Media.mobile([padding2(~v=`px(10), ~h=`px(12)), height(`px(120))]),
     ]);
 
   let bgCard = (url: string) =>
@@ -119,7 +119,7 @@ let make = (~latestBlockSub: Sub.t(BlockSub.t)) => {
         }
       />
       <div className={Css.merge([CssHelper.flexBox(), Styles.creditContaier])}>
-        <Text value="Empowered by" size=Text.Sm color=Colors.gray7 />
+        <Text value="Powered by" size=Text.Sm color=Colors.gray7 />
         <HSpacing size=Spacing.xs />
         // TODO: make it to link later
         <Text value="Band Oracle" size=Text.Sm color=Colors.bandBlue weight=Text.Medium />
```

### scan/src/components/account/AccountIndexDelegations.re
```diff
@@ -127,7 +127,6 @@ let make = (~address) =>
              isMobile ? renderBodyMobile(delegation) : renderBody(delegation)
            })
          ->React.array}
-        <VSpacing size=Spacing.lg />
         <Pagination currentPage=page pageCount onPageChange={newPage => setPage(_ => newPage)} />
       </>
     </div>
```

### scan/src/components/account/AccountIndexRedelegate.re
```diff
@@ -174,7 +174,6 @@ let make = (~address) =>
              isMobile ? renderBodyMobile(redelegateEntry) : renderBody(redelegateEntry)
            )
          ->React.array}
-        <VSpacing size=Spacing.lg />
         <Pagination currentPage=page pageCount onPageChange={newPage => setPage(_ => newPage)} />
       </>
     </div>
```
