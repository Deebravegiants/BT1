# [?] fix(monitor-v2): prevent V8 crash in Polymarket notifier with bounded event processing (#4922)

## Summary
Severity: Unknown
Chain: UMA
Component: UMAprotocol/protocol
Published: 2026-01-23
Source: https://github.com/UMAprotocol/protocol/commit/1dc14dccd08d266693349fe3e5d84a915e9d8d2c
Type: security-commit

## Details
fix(monitor-v2): prevent V8 crash in Polymarket notifier with bounded event processing (#4922)

Co-authored-by: Reinis Martinsons <77973553+Reinis-FRP@users.noreply.github.com>

## Patch
### packages/monitor-v2/src/monitor-polymarket/MonitorProposalsOrderBook.ts
```diff
@@ -11,6 +11,7 @@ import {
   calculatePolymarketQuestionID,
   decodeMultipleQueryPriceAtIndex,
   decodeMultipleValuesQuery,
+  fetchOrderFilledEventsBounded,
   getNotifiedProposals,
   getOrderFilledEvents,
   getPolymarketMarketInformation,
@@ -20,10 +21,12 @@ import {
   getProposalKeyToStore,
   getSportsMarketData,
   getSportsPayouts,
+  isDiscrepantTrade,
   isUnresolvable,
   isProposalNotified,
   ONE_SCALED,
   POLYGON_BLOCKS_PER_HOUR,
+  PolymarketTradeInformation,
   shouldIgnoreThirdPartyProposal,
   storeNotifiedProposals,
   Logger,
@@ -35,8 +38,6 @@ import {
   PolymarketMarketGraphqlProcessed,
   isInitialConfirmationLogged,
   fetchLatestAIDeepLink,
-  OrderFilledEventWithTrade,
-  fetchOrderFilledEvents,
 } from "./common";
 import * as common from "./common";
 
@@ -51,10 +52,7 @@ function getThresholds() {
 
 const blocksPerSecond = POLYGON_BLOCKS_PER_HOUR / 3_600;
 type ProposalProcessingContext = {
-  currentBlock?: number;
-  lookbackBlocks?: number;
-  gapBlocks?: number;
-  orderFilledEvents?: OrderFilledEventWithTrade[];
+  boundedTradesMap: Map<string, PolymarketTradeInformation[]>;
   aiDeeplink?: string;
 };
 
@@ -107,18 +105,11 @@ export async function processProposal(
   orderbooks: Record<string, MarketOrderbook>,
   params: MonitoringParams,
   logger: typeof Logger,
-  context?: ProposalProcessingContext
+  context: ProposalProcessingContext
 ): Promise<boolean /* notified */> {
   const thresholds = getThresholds();
   const isSportsRequest = proposal.requester === params.ctfSportsOracleAddress;
-
-  const currentBlock = context?.currentBlock ?? (await params.provider.getBlockNumber());
-  const lookbackBlocks = context?.lookbackBlocks ?? Math.round(params.fillEventsLookbackSeconds * blocksPerSecond);
-  const gapBlocks = context?.gapBlocks ?? Math.round(params.fillEventsProposalGapSeconds * blocksPerSecond);
-  const proposalGapStartBlock = Number(proposal.proposalBlockNumber) + gapBlocks;
-
-  // Use AI deeplink from context (fetched in advance)
-  const aiDeeplink = context?.aiDeeplink;
+  const aiDeeplink = context.aiDeeplink;
 
   const checkMarket = async (market: PolymarketMarketGraphqlProcessed): Promise<boolean> => {
     const outcome = isSportsRequest
@@ -135,14 +126,10 @@ export async function processProposal(
     const sellingWinnerSide = books[outcome.winner].asks.find((a) => a.price < thresholds.asks);
     const buyingLoserSide = books[outcome.loser].bids.find((b) => b.price > thresholds.bids);
 
-    const fromBlock = Math.max(proposalGapStartBlock, currentBlock - lookbackBlocks);
-    const fills = await getOrderFilledEvents(params, market.clobTokenIds, fromBlock, {
-      cachedEvents: context?.orderFilledEvents,
-      toBlock: currentBlock,
-    });
+    const fills = getOrderFilledEvents(market.clobTokenIds, context.boundedTradesMap);
 
-    const soldWinner = fills[outcome.winner].filter((f) => f.type === "sell" && f.price < thresholds.asks);
-    const boughtLoser = fills[outcome.loser].filter((f) => f.type === "buy" && f.price > thresholds.bids);
+    const soldWinner = fills[outcome.winner].filter((f) => isDiscrepantTrade(f, "winner", thresholds));
+    const boughtLoser = fills[outcome.loser].filter((f) => isDiscrepantTrade(f, "loser", thresholds));
 
     let alerted = false;
 
@@ -339,18 +326,44 @@ export async function monitorTransactionsProposedOrderBook(
   );
   const earliestFromBlock = Math.min(...fromBlocks);
 
-  // Flatten all clobTokenIds from all markets in all active bundles into a Set
-  const activeTokenIds = new Set<string>();
-  activeBundles.forEach((bundle) => {
-    bundle.markets.forEach((market) => {
-      activeTokenIds.add(market.clobTokenIds[0]);
-      activeTokenIds.add(market.clobTokenIds[1]);
-    });
-  });
+  // Pre-compute winner/loser for each market to enable targeted event filtering
+  const winnerTokenIds = new Set<string>();
+  const loserTokenIds = new Set<string>();
+
+  await Promise.all(
+    activeBundles.map(async ({ proposal, markets }) => {
+      const isSportsRequest = proposal.requester === params.ctfSportsOracleAddress;
+
+      await Promise.all(
+        markets.map(async (market) => {
+          const outcome = isSportsRequest
+            ? outcomeIndexes(true, proposal, await getSportsMarketData(params, market.questionID))
+            : outcomeIndexes(false, proposal);
 
-  const orderFilledEventsPromise = fetchOrderFilledEvents(params, earliestFromBlock, currentBlock, activeTokenIds);
+          // Skip draw/unresolvable outcomes
+          if (outcome.winner === -1) return;
 
-  // Fetch all AI deeplinks in advance and store in memory
+          winnerTokenIds.add(market.clobTokenIds[outcome.winner]);
+          loserTokenIds.add(market.clobTokenIds[outcome.loser]);
+        })
+      );
+    })
+  );
+
+  // Fetch OrderFilled events with bounded memory to prevent V8 crashes
+  // Only collect sells for winner tokens and buys for loser tokens
+  const thresholds = getThresholds();
+  const boundedTradesMapPromise = fetchOrderFilledEventsBounded(
+    params,
+    earliestFromBlock,
+    currentBlock,
+    winnerTokenIds,
+    loserTokenIds,
+    { asks: thresholds.asks, bids: thresholds.bids },
+    params.maxTradesPerToken
+  );
+
+  // Fetch all AI deeplinks in advance
   const aiDeeplinksMap = new Map<string, string>();
   await Promise.all(
     activeBundles.map(async ({ proposal }) => {
@@ -370,17 +383,15 @@ export async function monitorTransactionsProposedOrderBook(
     })
   );
 
+  const boundedTradesMap = await boundedTradesMapPromise;
+
   await BluebirdPromise.map(
     activeBundles,
     async ({ proposal, markets }) => {
       try {
-        const sharedOrderFilledEvents = await orderFilledEventsPromise;
         const aiDeeplink = aiDeeplinksMap.get(getProposalKeyToStore(proposal));
         const alerted = await processProposal(proposal, markets, orderbookMap, params, logger, {
-          currentBlock,
-          lookbackBlocks,
-          gapBlocks,
-          orderFilledEvents: sharedOrderFilledEvents,
+          boundedTradesMap,
           aiDeeplink,
         });
         if (alerted) await persistNotified(proposal, logger);
```

### packages/monitor-v2/src/monitor-polymarket/common.ts
```diff
@@ -3,7 +3,6 @@ import { createHttpClient } from "@uma/toolkit";
 import { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
 export const paginatedEventQuery = umaPaginatedEventQuery;
 
-import { Promise as BluebirdPromise } from "bluebird";
 import type { Provider } from "@ethersproject/abstract-provider";
 
 import { BigNumber, Contract, Event, EventFilter, ethers } from "ethers";
@@ -38,6 +37,25 @@ export const ONE_SCALED = ethers.utils.parseUnits("1", 18);
 
 export const POLYGON_BLOCKS_PER_HOUR = 1800;
 
+/**
+ * Determines if a trade represents a discrepancy based on token role and thresholds.
+ * - Winner tokens: discrepancy if selling below asks threshold (selling cheap when should win)
+ * - Loser tokens: discrepancy if buying above bids threshold (buying expensive when should lose)
+ */
+export const isDiscrepantTrade = (
+  trade: { type: "buy" | "sell"; price: number },
+  tokenRole: "winner" | "loser",
+  thresholds: { asks: number; bids: number }
+): boolean => {
+  if (tokenRole === "winner") {
+    return trade.type === "sell" && trade.price < thresholds.asks;
+  }
+  if (tokenRole === "loser") {
+    return trade.type === "buy" && trade.price > thresholds.bids;
+  }
+  return false;
+};
+
 // Get Polymarket initializer whitelist from env
 const getPolymarketInitializerWhitelist = (): string[] => {
   const envWhitelist = process.env.POLYMARKET_INITIALIZER_WHITELIST;
@@ -85,7 +103,8 @@ export interface MonitoringParams {
   proposalProcessingConcurrency: number;
   marketProcessingConcurrency: number;
   paginatedEventQueryConcurrency: number;
-  orderFilledEventsProcessingConcurrency: number;
+  maxTradesPerToken: number;
+  fillEventsChunkBlocks: number;
 }
 interface PolymarketMarketGraphql {
   question: string;
@@ -112,13 +131,6 @@ export interface PolymarketTradeInformation {
   timestamp: number;
 }
 
-export interface OrderFilledEventWithTrade {
-  blockNumber: number;
-  makerAssetId: string;
-  takerAssetId: string;
-  trade: PolymarketTradeInformation;
-}
-
 export interface PolymarketOrderBook {
   market: string;
   asset_id: string;
@@ -388,7 +400,13 @@ export const getPolymarketMarketInformation = async (
   });
 };
 
-const getTradeInfoFromOrderFilledEvent = async (
+/**
+ * Extracts trade info from an OrderFilled event, from the MAKER's perspective.
+ * - If maker provided USDC (makerAssetId=0), they were BUYING tokens
+ * - If maker provided tokens, they were SELLING tokens
+ * The caller should derive the taker's perspective by flipping the type.
+ */
+const getMakerTradeInfoFromOrderFilledEvent = async (
   provider: Provider,
   event: any,
   blockTimestamp?: number
@@ -407,103 +425,114 @@ const getTradeInfoFromOrderFilledEvent = async (
   };
 };
 
-export const fetchOrderFilledEvents = async (
+/**
+ * Fetch OrderFilled events with bounded memory
+ *
+ * @param winnerTokenIds - Token IDs where we only care about sells below asks threshold
+ * @param loserTokenIds - Token IDs where we only care about buys above bids threshold
+ * @returns Map of tokenId -> trades for that token
+ */
+export const fetchOrderFilledEventsBounded = async (
   params: MonitoringParams,
   startBlockNumber: number,
-  endBlockNumber?: number,
-  tokenIds?: Set<string> | string[]
-): Promise<OrderFilledEventWithTrade[]> => {
+  endBlockNumber: number,
+  winnerTokenIds: Set<string>,
+  loserTokenIds: Set<string>,
+  thresholds: { asks: number; bids: number },
+  maxTradesPerToken = 50
+): Promise<Map<string, PolymarketTradeInformation[]>> => {
   const ctfExchange = new ethers.Contract(
     params.ctfExchangeAddress,
     require("./abi/ctfExchange.json"),
     params.provider
   );
 
-  const toBlock = endBlockNumber ?? (await params.provider.getBlockNumber());
-  const searchConfig = {
-    fromBlock: startBlockNumber,
-    toBlock,
-    maxBlockLookBack: params.maxBlockLookBack,
-  };
-
-  // Create a Set for efficient tokenId lookups if provided
-  const tokenIdsSet = tokenIds ? (tokenIds instanceof Set ? tokenIds : new Set(tokenIds)) : undefined;
-
-  // Filter events early during batch fetching to reduce memory usage
-  const eventFilter = tokenIdsSet
-    ? (event: Event) => {
-        const makerAssetId = event?.args?.makerAssetId?.toString();
-        const takerAssetId = event?.args?.takerAssetId?.toString();
-        return tokenIdsSet.has(makerAssetId) || tokenIdsSet.has(takerAssetId);
-      }
-    : undefined;
+  const result = new Map<string, PolymarketTradeInformation[]>();
+  const blockTimestamps = new Map<number, number>();
 
-  const events: Event[] = await paginatedEventQuery(
-    ctfExchange,
-    ctfExchange.filters.OrderFilled(null, null, null, null, null, null, null, null),
-    searchConfig,
-    params.retryAttempts,
-    queryFilterSafe,
-    eventFilter
-  );
+  // Combine all token IDs for the event filter
+  const allTokenIds = new Set([...winnerTokenIds, ...loserTokenIds]);
 
-  const blockTimestamps = new Map<number, number>();
   const getTimestamp = async (blockNumber: number): Promise<number> => {
     if (!blockTimestamps.has(blockNumber)) {
       blockTimestamps.set(blockNumber, (await params.provider.getBlock(blockNumber)).timestamp);
     }
     return blockTimestamps.get(blockNumber)!;
   };
 
-  return BluebirdPromise.map(
-    events,
-    async (event) => {
-      const blockTimestamp = await getTimestamp(event.blockNumber);
-      return {
-        blockNumber: event.blockNumber,
-        makerAssetId: event?.args?.makerAssetId.toString(),
-        takerAssetId: event?.args?.takerAssetId.toString(),
-        trade: await getTradeInfoFromOrderFilledEvent(params.provider, event, blockTimestamp),
-      };
-    },
-    { concurrency: params.orderFilledEventsProcessingConcurrency }
-  );
-};
+  // Helper to determine token role and check if trade is a discrepancy
+  const isDiscrepancyRelevant = (tokenId: string, type: "buy" | "sell", price: number): boolean => {
+    const tokenRole = winnerTokenIds.has(tokenId) ? "winner" : loserTokenIds.has(tokenId) ? "loser" : null;
+    if (!tokenRole) return false;
+    return isDiscrepantTrade({ type, price }, tokenRole, thresholds);
+  };
 
-export const filterOrderFilledEvents = (
-  orderFilledEvents: OrderFilledEventWithTrade[],
-  clobTokenIds: [string, string],
-  startBlockNumber: number
-): [PolymarketTradeInformation[], PolymarketTradeInformation[]] => {
-  const [tokenOne, tokenTwo] = clobTokenIds;
-  const eventsWithinWindow = orderFilledEvents.filter((event) => event.blockNumber >= startBlockNumber);
+  const addTrade = (tokenId: string, trade: PolymarketTradeInformation): void => {
+    let trades = result.get(tokenId);
+    if (!trades) {
+      trades = [];
+      result.set(tokenId, trades);
+    }
+    if (trades.length < maxTradesPerToken) {
+      trades.push(trade);
+    }
+  };
 
-  const outcomeTokenOne = eventsWithinWindow
-    .filter((event) => [event.takerAssetId, event.makerAssetId].includes(tokenOne))
-    .map((event) => event.trade);
+  const eventFilter = (event: Event): boolean => {
+    const makerAssetId = event?.args?.makerAssetId?.toString();
+    const takerAssetId = event?.args?.takerAssetId?.toString();
+    return allTokenIds.has(makerAssetId) || allTokenIds.has(takerAssetId);
+  };
 
-  const outcomeTokenTwo = eventsWithinWindow
-    .filter((event) => [event.takerAssetId, event.makerAssetId].includes(tokenTwo))
-    .map((event) => event.trade);
+  // Process in chunks to avoid accumulating all events in memory
+  for (let fromBlock = startBlockNumber; fromBlock <= endBlockNumber; fromBlock += params.fillEventsChunkBlocks) {
+    const toBlock = Math.min(fromBlock + params.fillEventsChunkBlocks - 1, endBlockNumber);
+
+    const events = await paginatedEventQuery(
+      ctfExchange,
+      ctfExchange.filters.OrderFilled(null, null, null, null, null, null, null, null),
+      { fromBlock, toBlock, maxBlockLookBack: 0 }, // Disable internal pagination - we chunk externally
+      params.retryAttempts,
+      queryFilterSafe,
+      eventFilter
+    );
 
-  return [outcomeTokenOne, outcomeTokenTwo];
-};
+    // Process and aggregate immediately, then discard raw events
+    for (const event of events) {
+      if (!event.args) continue;
+      const makerAssetId = event.args.makerAssetId.toString();
+      const outcomeTokenId = makerAssetId === "0" ? event.args.takerAssetId.toString() : makerAssetId;
 
-export const getOrderFilledEvents = async (
-  params: MonitoringParams,
-  clobTokenIds: [string, string],
-  startBlockNumber: number,
-  opts?: {
-    toBlock?: number;
-    cachedEvents?: OrderFilledEventWithTrade[];
+      if (!allTokenIds.has(outcomeTokenId)) continue;
+
+      const timestamp = await getTimestamp(event.blockNumber);
+      const trade = await getMakerTradeInfoFromOrderFilledEvent(params.provider, event, timestamp);
+
+      // Check both sides of the trade: maker's perspective and taker's perspective
+      // trade.type is from maker's POV; takerType is the opposite
+      // With context-aware filtering, only ONE side will ever match per trade:
+      // - Winner token: captures sells (either maker or taker selling)
+      // - Loser token: captures buys (either maker or taker buying)
+      if (isDiscrepancyRelevant(outcomeTokenId, trade.type, trade.price)) {
+        addTrade(outcomeTokenId, trade);
+      }
+
+      const takerType: "buy" | "sell" = trade.type === "buy" ? "sell" : "buy";
+      if (isDiscrepancyRelevant(outcomeTokenId, takerType, trade.price)) {
+        addTrade(outcomeTokenId, { ...trade, type: takerType });
+      }
+    }
   }
-): Promise<[PolymarketTradeInformation[], PolymarketTradeInformation[]]> => {
-  // Pass tokenIds to fetchOrderFilledEvents to filter events early during batch fetching
-  const tokenIdsSet = new Set(clobTokenIds);
-  const orderFilledEvents =
-    opts?.cachedEvents ?? (await fetchOrderFilledEvents(params, startBlockNumber, opts?.toBlock, tokenIdsSet));
 
-  return filterOrderFilledEvents(orderFilledEvents, clobTokenIds, startBlockNumber);
+  return result;
+};
+
+export const getOrderFilledEvents = (
+  clobTokenIds: [string, string],
+  boundedTradesMap: Map<string, PolymarketTradeInformation[]>
+): [PolymarketTradeInformation[], PolymarketTradeInformation[]] => {
+  const [tokenOne, tokenTwo] = clobTokenIds;
+  return [boundedTradesMap.get(tokenOne) ?? [], boundedTradesMap.get(tokenTwo) ?? []];
 };
 
 export const calculatePolymarketQuestionID = (ancillaryData: string): string => {
@@ -754,7 +783,7 @@ export interface UMAAIRetry {
   data: {
     input: {
       timing?: {
-        expiration_timestamp?: number;
+        expiration_time?: string;
       };
     };
   };
@@ -799,9 +828,12 @@ export async function fetchLatestAIDeepLink(
     );
     const duration = Date.now() - startTime;
 
-    const result = response.data?.elements?.find(
-      (element) => element.data.input.timing?.expiration_timestamp === proposal.proposalExpirationTimestamp.toNumber()
-    );
+    const result = response.data?.elements?.find((element) => {
+      const expirationTime = element.data.input.timing?.expiration_time;
+      if (!expirationTime) return false;
+      const expirationTimestamp = Math.floor(new Date(expirationTime).getTime() / 1000);
+      return expirationTimestamp === proposal.proposalExpirationTimestamp.toNumber();
+    });
 
     if (!result) {
       logger.debug({
@@ -1018,9 +1050,10 @@ export const initMonitoringParams = async (
     ? Number(env.PAGINATED_EVENT_QUERY_CONCURRENCY)
     : 25; // default to 25 concurrent paginated event queries
 
-  const orderFilledEventsProcessingConcurrency = env.ORDER_FILLED_EVENTS_PROCESSING_CONCURRENCY
-    ? Number(env.ORDER_FILLED_EVENTS_PROCESSING_CONCURRENCY)
-    : 25; // default to 25 concurrent order filled events processing
+  const maxTradesPerToken = env.MAX_TRADES_PER_TOKEN ? Number(env.MAX_TRADES_PER_TOKEN) : 50;
+
+  // Chunk size for bounded event fetching (~1 minute on Polygon at 30 blocks/min)
+  const fillEventsChunkBlocks = env.FILL_EVENTS_CHUNK_BLOCKS ? Number(env.FILL_EVENTS_CHUNK_BLOCKS) : 30;
 
   const maxConcurrentRequests = env.MAX_CONCURRENT_REQUESTS ? Number(env.MAX_CONCURRENT_REQUESTS) : 5;
   const minTimeBetweenRequests = env.MIN_TIME_BETWEEN_REQUESTS ? Number(env.MIN_TIME_BETWEEN_REQUESTS) : 200;
@@ -1112,7 +1145,8 @@ export const initMonitoringParams = async (
     proposalProcessingConcurrency,
     marketProcessingConcurrency,
     paginatedEventQueryConcurrency,
-    orderFilledEventsProcessingConcurrency,
+    maxTradesPerToken,
+    fillEventsChunkBlocks,
   };
 };
 
```

### packages/monitor-v2/test/PolymarketMonitor.ts
```diff
@@ -26,10 +26,7 @@ import {
   PolymarketTradeInformation,
   Underdog,
 } from "../src/monitor-polymarket/common";
-import {
-  monitorTransactionsProposedOrderBook,
-  processProposal,
-} from "../src/monitor-polymarket/MonitorProposalsOrderBook";
+import { monitorTransactionsProposedOrderBook } from "../src/monitor-polymarket/MonitorProposalsOrderBook";
 import { tryHexToUtf8String } from "../src/utils/contracts";
 import { umaEcosystemFixture } from "./fixtures/UmaEcosystem.Fixture";
 import { formatBytes32String, getContractFactory, hre, Provider, Signer, toUtf8Bytes } from "./utils";
@@ -44,7 +41,6 @@ describe("PolymarketNotifier", function () {
   let deployer: Signer;
   let votingToken: VotingTokenEthers;
   let getNotifiedProposalsStub: sinon.SinonStub;
-  let fetchOrderFilledEventsStub: sinon.SinonStub;
   const identifier = formatBytes32String("TEST_IDENTIFIER");
   const ancillaryData = toUtf8Bytes(`q:"Really hard question, maybe 100, maybe 90?"`);
 
@@ -124,7 +120,8 @@ describe("PolymarketNotifier", function () {
       proposalProcessingConcurrency: 5,
       marketProcessingConcurrency: 3,
       paginatedEventQueryConcurrency: 5,
-      orderFilledEventsProcessingConcurrency: 25,
+      maxTradesPerToken: 50,
+      fillEventsChunkBlocks: 30,
     };
   };
 
@@ -174,7 +171,6 @@ describe("PolymarketNotifier", function () {
     sandbox.stub(commonModule, "isProposalNotified").resolves(false);
 
     sandbox.stub(commonModule, "fetchLatestAIDeepLink").resolves({ deeplink: undefined });
-    fetchOrderFilledEventsStub = sandbox.stub(commonModule, "fetchOrderFilledEvents").resolves([]);
 
     // Fund staker and stake tokens.
     const TEN_MILLION = ethers.utils.parseEther("10000000");
@@ -193,6 +189,12 @@ describe("PolymarketNotifier", function () {
     sandbox.stub(commonModule, functionName).callsFake(mockDataFunction);
   }
 
+  function mockSyncFunctionWithReturnValue(functionName: CommonModuleFunctions, mockValue: any) {
+    const mockDataFunction = sandbox.stub();
+    mockDataFunction.returns(mockValue);
+    sandbox.stub(commonModule, functionName).callsFake(mockDataFunction);
+  }
+
   function mockFunctionThrowsError(functionName: CommonModuleFunctions, errorMessage = "Mock error") {
     const mockDataFunction = sandbox.stub();
     mockDataFunction.rejects(new Error(errorMessage));
@@ -242,7 +244,7 @@ describe("PolymarketNotifier", function () {
 
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(orders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -285,7 +287,7 @@ describe("PolymarketNotifier", function () {
       // Default stubs common to these tests
       sandbox.stub(commonModule, "getPolymarketMarketInformation").resolves(marketInfo);
       sandbox.stub(commonModule, "getPolymarketOrderBooks").resolves(asBooksRecord(emptyOrders));
-      sandbox.stub(commonModule, "getOrderFilledEvents").resolves([[], []]);
+      sandbox.stub(commonModule, "getOrderFilledEvents").returns([[], []]);
     });
 
     it("First check, no discrepancy → summary only; flag set.", async function () {
@@ -418,7 +420,7 @@ describe("PolymarketNotifier", function () {
   it("It should not notify if order book is empty", async function () {
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     const spy = sinon.spy();
     const spyLogger = createNewLogger([new SpyTransport({}, { spy: spy })]);
@@ -442,7 +444,7 @@ describe("PolymarketNotifier", function () {
     ];
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
-    mockFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -482,7 +484,7 @@ describe("PolymarketNotifier", function () {
     ];
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
-    mockFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -511,7 +513,7 @@ describe("PolymarketNotifier", function () {
   it("It should notify if there are proposals with high volume", async function () {
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", [{ ...marketInfo[0], volumeNum: 2_000_000 }]);
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -541,7 +543,7 @@ describe("PolymarketNotifier", function () {
 
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(orders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -581,7 +583,7 @@ describe("PolymarketNotifier", function () {
 
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", [{ ...marketInfo[0], volumeNum: 2_000_000 }]);
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -615,7 +617,7 @@ describe("PolymarketNotifier", function () {
 
   it("It should notify if market polymarket information is not found", async function () {
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
     mockFunctionThrowsError("getPolymarketMarketInformation", "Market not found");
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
@@ -671,7 +673,7 @@ describe("PolymarketNotifier", function () {
     });
 
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     // Calculate the actual questionID that will be generated from our ancillary data
     const expectedQuestionID = ethers.utils.keccak256(ancillaryDataHex);
@@ -717,7 +719,7 @@ describe("PolymarketNotifier", function () {
     });
 
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
-    mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
 
     // Calculate the actual questionID that will be generated from our ancillary data
     const expectedQuestionID = ethers.utils.keccak256(ethers.utils.hexlify(ancillaryData));
@@ -753,7 +755,7 @@ describe("PolymarketNotifier", function () {
     ];
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
-    mockFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     const tx = await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -788,7 +790,7 @@ describe("PolymarketNotifier", function () {
 
     mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(emptyOrders));
     mockFunctionWithReturnValue("getPolymarketMarketInformation", [{ ...marketInfo[0], volumeNum: 2_000_000 }]);
-    mockFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
+    mockSyncFunctionWithReturnValue("getOrderFilledEvents", orderFilledEvents);
 
     await oov2.requestPrice(identifier, 1, ancillaryData, votingToken.address, 0);
     await oov2.proposePrice(await deployer.getAddress(), identifier, 1, ancillaryData, ONE);
@@ -863,7 +865,7 @@ describe("PolymarketNotifier", function () {
         },
       ];
       mockFunctionWithReturnValue("getPolymarketOrderBooks", asBooksRecord(sportsOrderBook));
-      mockFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
+      mockSyncFunctionWithReturnValue("getOrderFilledEvents", emptyTradeInformation);
       mockFunctionWithReturnValue("getPolymarketMarketInformation", marketInfo);
 
       const spy = sinon.spy();
@@ -1054,103 +1056,6 @@ describe("PolymarketNotifier", function () {
     });
   });
 
-  describe("processProposal proposal gap", function () {
-    it("applies the default proposal gap when the lookback window would include the proposal block", async function () {
-      const params = await createMonitoringParams();
-      params.fillEventsLookbackSeconds = 7_200; // 2 hours
-
-      const currentBlock = 2_000;
-      const getBlockNumberStub = sandbox.stub().resolves(currentBlock);
-      params.provider = ({ getBlockNumber: getBlockNumberStub } as unknown) as Provider;
-
-      const proposalBlockNumber = 900;
-      const proposal: OptimisticPriceRequest = {
-        proposalHash: "0xdefaultgap",
-        requester: params.additionalRequesters[0],
-        proposer: await deployer.getAddress(),
-        identifier,
-        proposedPrice: ONE,
-        requestTimestamp: ethers.BigNumber.from(Date.now()),
-        proposalBlockNumber,
-        ancillaryData: ethers.utils.hexlify(ancillaryData),
-        requestHash: "0xdefaultgaprequest",
-        requestLogIndex: 0,
-        proposalTimestamp: ethers.BigNumber.from(Date.now()),
-        proposalExpirationTimestamp: ethers.BigNumber.from(Date.now() + 3_600),
-        proposalLogIndex: 0,
-      };
-
-      let capturedFromBlock: number | undefined;
-      sandbox.stub(commonModule, "getOrderFilledEvents").callsFake(async (_params, _tokenIds, fromBlock) => {
-        capturedFromBlock = fromBlock;
-        return emptyTradeInformation;
-      });
-
-      sandbox.stub(commonModule, "isInitialConfirmationLogged").resolves(false);
-      sandbox.stub(commonModule, "markInitialConfirmationLogged").resolves();
-
-      const logger = createNewLogger([new SpyTransport({}, { spy: sinon.spy() })]);
-
-      await processProposal(proposal, marketInfo, asBooksRecord(emptyOrders), params, logger);
-
-      assert.isDefined(capturedFromBlock, "getOrderFilledEvents should be called");
-      const blocksPerSecond = commonModule.POLYGON_BLOCKS_PER_HOUR / 3_600;
-      const expectedFromBlock = Math.max(
-        proposalBlockNumber + Math.round(params.fillEventsProposalGapSeconds * blocksPerSecond),
-        currentBlock - Math.round(params.fillEventsLookbackSeconds * blocksPerSecond)
-      );
-      assert.equal(capturedFromBlock, expectedFromBlock);
-    });
-
-    it("uses the configured proposal gap when provided", async function () {
-      const params = await createMonitoringParams();
-      params.fillEventsLookbackSeconds = 7_200;
-      params.fillEventsProposalGapSeconds = 600; // 10 minutes
-
-      const currentBlock = 2_000;
-      const getBlockNumberStub = sandbox.stub().resolves(currentBlock);
-      params.provider = ({ getBlockNumber: getBlockNumberStub } as unknown) as Provider;
-
-      const proposalBlockNumber = 900;
-      const proposal: OptimisticPriceRequest = {
-        proposalHash: "0xcustomgap",
-        requester: params.additionalRequesters[0],
-        proposer: await deployer.getAddress(),
-        identifier,
-        proposedPrice: ONE,
-        requestTimestamp: ethers.BigNumber.from(Date.now()),
-        proposalBlockNumber,
-        ancillaryData: ethers.utils.hexlify(ancillaryData),
-        requestHash: "0xcustomgaprequest",
-        requestLogIndex: 0,
-        proposalTimestamp: ethers.BigNumber.from(Date.now()),
-        proposalExpirationTimestamp: ethers.BigNumber.from(Date.now() + 3_600),
-        proposalLogIndex: 0,
-      };
-
-      let capturedFromBlock: number | undefined;
-      sandbox.stub(commonModule, "getOrderFilledEvents").callsFake(async (_params, _tokenIds, fromBlock) => {
-        capturedFromBlock = fromBlock;
-        return emptyTradeInformation;
-      });
-
-      sandbox.stub(commonModule, "isInitialConfirmationLogged").resolves(false);
-      sandbox.stub(commonModule, "markInitialConfirmationLogged").resolves();
-
-      const logger = createNewLogger([new SpyTransport({}, { spy: sinon.spy() })]);
-
-      await processProposal(proposal, marketInfo, asBooksRecord(emptyOrders), params, logger);
-
-      assert.isDefined(capturedFromBlock, "getOrderFilledEvents should be called");
-      const blocksPerSecond = commonModule.POLYGON_BLOCKS_PER_HOUR / 3_600;
-      const expectedFromBlock = Math.max(
-        proposalBlockNumber + Math.round(params.fillEventsProposalGapSeconds * blocksPerSecond),
-        currentBlock - Math.round(params.fillEventsLookbackSeconds * blocksPerSecond)
-      );
-      assert.equal(capturedFromBlock, expectedFromBlock);
-    });
-  });
-
   it("fetches OrderFilled events once using the earliest fromBlock across proposals", async function () {
     const params = await createMonitoringParams();
     params.fillEventsLookbackSeconds = 7_200;
@@ -1188,7 +1093,9 @@ describe("PolymarketNotifier", function () {
       Math.max(proposalB.proposalBlockNumber + gapBlocks, currentBlock - lookbackBlocks)
     );
 
-    fetchOrderFilledEventsStub.resetHistory();
+    // Stub fetchOrderFilledEventsBounded to return an empty map
+    const boundedTradesMap = new Map<string, PolymarketTradeInformation[]>();
+    const fetchBoundedStub = sandbox.stub(commonModule, "fetchOrderFilledEventsBounded").resolves(boundedTradesMap);
 
     sandbox
       .stub(commonModule, "getPolymarketProposedPriceRequestsOO")
@@ -1203,55 +1110,18 @@ describe("PolymarketNotifier", function () {
     const logger = createNewLogger([new SpyTransport({}, { spy: sinon.spy() })]);
     await monitorTransactionsProposedOrderBook(logger, params);
 
-    sinon.assert.calledOnce(fetchOrderFilledEventsStub);
-    // fetchOrderFilledEvents now takes activeTokenIds as 4th parameter
-    const expectedTokenIds = new Set(marketInfo[0].clobTokenIds);
-    sinon.assert.calledWithExactly(
-      fetchOrderFilledEventsStub,
-      params,
-      expectedEarliestFromBlock,
-      currentBlock,
-      expectedTokenIds
-    );
-    assert.equal(getOrderFilledEventsSpy.callCount, 2, "fills are filtered per proposal");
-    const cachedEventsArgs = getOrderFilledEventsSpy.getCalls().map((call) => call.args[3]?.cachedEvents);
-    assert.isDefined(cachedEventsArgs[0], "cached events are forwarded into per-market filters");
-    assert.strictEqual(cachedEventsArgs[0], cachedEventsArgs[1], "shared event cache is reused across proposals");
-  });
-
-  it("getOrderFilledEvents uses the fillEventsLookbackSeconds", async function () {
-    const currentBlock = 100_000;
-    const fillEventsLookbackSeconds = 3_600; // 1 hour
-    const proposalBlockNumber = 95_000; // anchor block
-
-    const params = await createMonitoringParams();
-    params.fillEventsLookbackSeconds = fillEventsLookbackSeconds;
-
-    const providerStub = new ethers.providers.JsonRpcProvider();
-    sandbox.stub(providerStub, "getBlockNumber").resolves(currentBlock);
-    params.provider = providerStub as any;
-
-    const lookbackBlocks = Math.round((fillEventsLookbackSeconds * commonModule.POLYGON_BLOCKS_PER_HOUR) / 3_600);
-    const fromBlockParam = Math.max(proposalBlockNumber, currentBlock - lookbackBlocks);
-
-    // Restore the fetchOrderFilledEvents stub from beforeEach so we can test the real implementation
-    fetchOrderFilledEventsStub.restore();
+    sinon.assert.calledOnce(fetchBoundedStub);
+    // Verify fetchOrderFilledEventsBounded was called with correct earliest fromBlock
+    const callArgs = fetchBoundedStub.firstCall.args;
+    assert.equal(callArgs[1], expectedEarliestFromBlock, "earliest fromBlock passed to bounded fetch");
+    assert.equal(callArgs[2], currentBlock, "currentBlock passed to bounded fetch");
 
-    let capturedFromBlock: number | undefined;
-    sandbox.stub(commonModule, "paginatedEventQuery").callsFake(async (_c, _f, searchConfig) => {
-      capturedFromBlock = searchConfig.fromBlock;
-      return [];
-    });
-
-    sandbox.stub(ethers, "Contract").returns({ filters: { OrderFilled: () => ({ topics: [] }) } } as any);
-
-    await commonModule.getOrderFilledEvents(params, ["0xdeadbeef", "0xfeedface"], fromBlockParam);
-
-    assert.equal(
-      capturedFromBlock,
-      fromBlockParam,
-      "`fromBlock` passed to paginatedEventQuery must equal the caller-computed value"
-    );
+    // getOrderFilledEvents should be called for each proposal, using the boundedTradesMap
+    assert.equal(getOrderFilledEventsSpy.callCount, 2, "fills are filtered per proposal");
+    // The new signature is getOrderFilledEvents(clobTokenIds, boundedTradesMap), so args[1] is boundedTradesMap
+    const boundedMapArgs = getOrderFilledEventsSpy.getCalls().map((call) => call.args[1]);
+    assert.strictEqual(boundedMapArgs[0], boundedTradesMap, "bounded trades map is forwarded");
+    assert.strictEqual(boundedMapArgs[0], boundedMapArgs[1], "shared bounded map is reused across proposals");
   });
 
   describe("getPolymarketProposedPriceRequestsOO Filtering", function () {
@@ -1311,7 +1181,12 @@ describe("PolymarketNotifier", function () {
       const params = await createMonitoringParams();
       // Set the parameter to 120 seconds.
       params.checkBeforeExpirationSeconds = 120;
-      const result = await commonModule.getPolymarketProposedPriceRequestsOO(params, "v2", [fakeRequester]);
+      const result = await commonModule.getPolymarketProposedPriceRequestsOO(
+        params,
+        "v2",
+        [fakeRequester],
+        oov2.address
+      );
 
       // Expect that only the event with expirationTime fakeTime+100 (the "close-to-expiration" event) is returned.
       assert.equal(result.length, 1, "Expected one event to pass the expiration filter");
@@ -1325,4 +1200,33 @@ describe("PolymarketNotifier", function () {
       paginatedEventQueryStub.restore();
     });
   });
+
+  describe("Bounded OrderFilled Events", function () {
+    it("getOrderFilledEvents returns data from boundedTradesMap", function () {
+      const tokenIds: [string, string] = ["0xtoken1", "0xtoken2"];
+      const trades1: PolymarketTradeInformation[] = [{ price: 0.8, type: "sell", amount: 100, timestamp: 123 }];
+      const trades2: PolymarketTradeInformation[] = [{ price: 0.2, type: "buy", amount: 50, timestamp: 456 }];
+
+      const boundedTradesMap = new Map<string, PolymarketTradeInformation[]>();
+      boundedTradesMap.set(tokenIds[0], trades1);
+      boundedTradesMap.set(tokenIds[1], trades2);
+
+      const result = commonModule.getOrderFilledEvents(tokenIds, boundedTradesMap);
+
+      assert.deepEqual(result[0], trades1, "token1 trades returned");
+      assert.deepEqual(result[1], trades2, "token2 trades returned");
+    });
+
+    it("getOrderFilledEvents returns empty arrays for missing tokens in boundedTradesMap", function () {
+      const tokenIds: [string, string] = ["0xtoken1", "0xtoken2"];
+      const boundedTradesMap = new Map<string, PolymarketTradeInformation[]>();
+      // Only token1 has data
+      boundedTradesMap.set(tokenIds[0], [{ price: 0.8, type: "sell", amount: 100, timestamp: 123 }]);
+
+      const result = commonModule.getOrderFilledEvents(tokenIds, boundedTradesMap);
+
+      assert.equal(result[0].length, 1, "token1 has trades");
+      assert.deepEqual(result[1], [], "token2 returns empty array");
+    });
+  });
 });
```
