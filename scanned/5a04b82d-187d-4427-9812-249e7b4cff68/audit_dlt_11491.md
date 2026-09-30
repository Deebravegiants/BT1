# [?] Merge pull request #3547 from pyth-network/cprussin/fix-symbol-overflow

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2026-03-12
Source: https://github.com/pyth-network/pyth-crosschain/commit/e37020e12de3d369ca6ee009e1c9533d468ddc44
Type: security-commit

## Details
Merge pull request #3547 from pyth-network/cprussin/fix-symbol-overflow

fix(insights): fix missing feed names

## Patch
### apps/insights/src/components/PriceFeeds/price-feeds-card.module.scss
```diff
@@ -1,6 +1,10 @@
 @use "@pythnetwork/component-library/theme";
 
 .priceFeedsCard {
+  .symbol {
+    flex-grow: 1;
+  }
+
   .toolbar {
     .searchInput {
       flex-grow: 1;
```

### apps/insights/src/components/PriceFeeds/price-feeds-card.tsx
```diff
@@ -112,42 +112,43 @@ const ResolvedPriceFeedsCard = ({ priceFeeds, ...props }: Props) => {
           icon,
           assetClass,
         }) => ({
-          id: symbol,
-          href: `/price-feeds/${encodeURIComponent(symbol)}`,
-          textValue: displaySymbol,
           data: {
+            assetClass: <AssetClassBadge>{assetClass}</AssetClassBadge>,
+            confidenceInterval: (
+              <LiveConfidence cluster={Cluster.Pythnet} feedKey={key} />
+            ),
             exponent: (
               <LiveValue
-                field="exponent"
-                feedKey={key}
-                defaultValue={exponent}
                 cluster={Cluster.Pythnet}
+                defaultValue={exponent}
+                feedKey={key}
+                field="exponent"
               />
             ),
             numPublishers: (
               <LiveValue
-                field="numQuoters"
-                feedKey={key}
-                defaultValue={numQuoters}
                 cluster={Cluster.Pythnet}
+                defaultValue={numQuoters}
+                feedKey={key}
+                field="numQuoters"
               />
             ),
-            price: <LivePrice feedKey={key} cluster={Cluster.Pythnet} />,
-            confidenceInterval: (
-              <LiveConfidence feedKey={key} cluster={Cluster.Pythnet} />
+            price: <LivePrice cluster={Cluster.Pythnet} feedKey={key} />,
+            priceFeedId: (
+              <FeedKey className={styles.feedKey ?? ""} feedKey={key} />
             ),
             priceFeedName: (
               <SymbolPairTag
+                className={styles.symbol}
                 description={description}
                 displaySymbol={displaySymbol}
                 icon={icon}
               />
             ),
-            assetClass: <AssetClassBadge>{assetClass}</AssetClassBadge>,
-            priceFeedId: (
-              <FeedKey feedKey={key} className={styles.feedKey ?? ""} />
-            ),
           },
+          href: `/price-feeds/${encodeURIComponent(symbol)}`,
+          id: symbol,
+          textValue: displaySymbol,
         }),
       ),
     [paginatedItems],
@@ -173,21 +174,21 @@ const ResolvedPriceFeedsCard = ({ priceFeeds, ...props }: Props) => {
 
   return (
     <PriceFeedsCardContents
-      numResults={numResults}
-      search={search}
-      sortDescriptor={sortDescriptor}
       assetClass={assetClass}
       assetClasses={assetClasses}
+      mkPageLink={mkPageLink}
       numPages={numPages}
-      page={page}
-      pageSize={pageSize}
-      onSearchChange={updateSearch}
-      onSortChange={updateSortDescriptor}
+      numResults={numResults}
       onAssetClassChange={updateAssetClass}
-      onPageSizeChange={updatePageSize}
       onPageChange={updatePage}
-      mkPageLink={mkPageLink}
+      onPageSizeChange={updatePageSize}
+      onSearchChange={updateSearch}
+      onSortChange={updateSortDescriptor}
+      page={page}
+      pageSize={pageSize}
       rows={rows}
+      search={search}
+      sortDescriptor={sortDescriptor}
       {...props}
     />
   );
@@ -226,85 +227,85 @@ type PriceFeedsCardContents = Pick<Props, "id"> &
 
 const PriceFeedsCardContents = ({ id, ...props }: PriceFeedsCardContents) => (
   <Card
-    id={id}
-    icon={<ChartLine />}
     className={styles.priceFeedsCard}
+    icon={<ChartLine />}
+    id={id}
     title={
       <>
         <span>Price Feeds</span>
         {!props.isLoading && (
-          <Badge style="filled" variant="neutral" size="md">
+          <Badge size="md" style="filled" variant="neutral">
             {props.numResults}
           </Badge>
         )}
       </>
     }
-    toolbarClassName={styles.toolbar}
     toolbar={
       <>
         <SearchInput
+          className={styles.searchInput ?? ""}
+          placeholder="Feed symbol"
           size="sm"
           width={50}
-          placeholder="Feed symbol"
-          className={styles.searchInput ?? ""}
           {...(props.isLoading
-            ? { isPending: true, isDisabled: true }
+            ? { isDisabled: true, isPending: true }
             : {
-                value: props.search,
                 onChange: props.onSearchChange,
+                value: props.search,
               })}
         />
         <Select
+          hideLabel
           label="Asset Class"
           size="sm"
           variant="outline"
-          hideLabel
           {...(props.isLoading
-            ? { isPending: true, options: [], buttonLabel: "Asset Class" }
+            ? { buttonLabel: "Asset Class", isPending: true, options: [] }
             : {
+                buttonLabel:
+                  props.assetClass === "" ? "Asset Class" : props.assetClass,
+                hideGroupLabel: true,
+                onSelectionChange: props.onAssetClassChange,
                 optionGroups: [
                   { name: "All", options: [{ id: "" }] },
                   {
                     name: "Asset classes",
                     options: props.assetClasses.map((id) => ({ id })),
                   },
                 ],
-                hideGroupLabel: true,
-                show: ({ id }) => (id === "" ? "All" : id),
                 placement: "bottom end",
-                buttonLabel:
-                  props.assetClass === "" ? "Asset Class" : props.assetClass,
                 selectedKey: props.assetClass,
-                onSelectionChange: props.onAssetClassChange,
+                show: ({ id }) => (id === "" ? "All" : id),
               })}
         />
       </>
     }
+    toolbarClassName={styles.toolbar}
     {...(!props.isLoading && {
       footer: (
         <Paginator
-          numPages={props.numPages}
           currentPage={props.page}
+          mkPageLink={props.mkPageLink}
+          numPages={props.numPages}
           onPageChange={props.onPageChange}
-          pageSize={props.pageSize}
           onPageSizeChange={props.onPageSizeChange}
-          mkPageLink={props.mkPageLink}
+          pageSize={props.pageSize}
         />
       ),
     })}
   >
     <EntityList
-      label="Price Feeds"
       className={styles.entityList ?? ""}
-      headerLoadingSkeleton={<SymbolPairTag isLoading />}
       fields={[
         { id: "assetClass", name: "Asset Class" },
         { id: "priceFeedId", name: "Price Feed ID" },
         { id: "confidenceInterval", name: "Confidence Interval" },
         { id: "exponent", name: "Exponent" },
         { id: "numPublishers", name: "# Publishers" },
       ]}
+      headerLoadingSkeleton={<SymbolPairTag isLoading />}
       isLoading={props.isLoading}
+      label="Price Feeds"
       rows={
         props.isLoading
           ? []
@@ -320,78 +321,78 @@ const PriceFeedsCardContents = ({ id, ...props }: PriceFeedsCardContents) => (
       }
     />
     <Table
-      rounded
-      fill
-      label="Price Feeds"
-      stickyHeader="appHeader"
       className={styles.table ?? ""}
       columns={[
         {
+          alignment: "left",
+          allowsSorting: true,
           id: "priceFeedName",
-          name: "PRICE FEED",
           isRowHeader: true,
-          alignment: "left",
           loadingSkeleton: <SymbolPairTag isLoading />,
-          allowsSorting: true,
+          name: "PRICE FEED",
         },
         {
+          alignment: "left",
+          allowsSorting: true,
           id: "assetClass",
+          loadingSkeletonWidth: 20,
           name: "ASSET CLASS",
-          alignment: "left",
           width: 45,
-          loadingSkeletonWidth: 20,
-          allowsSorting: true,
         },
         {
+          alignment: "left",
           id: "priceFeedId",
+          loadingSkeletonWidth: 30,
           name: "PRICE FEED ID",
-          alignment: "left",
           width: 40,
-          loadingSkeletonWidth: 30,
         },
         {
+          alignment: "right",
           id: "price",
+          loadingSkeletonWidth: SKELETON_WIDTH,
           name: <PriceName uppercase />,
-          alignment: "right",
           width: 45,
-          loadingSkeletonWidth: SKELETON_WIDTH,
         },
         {
+          alignment: "left",
           id: "confidenceInterval",
+          loadingSkeletonWidth: SKELETON_WIDTH,
           name: "CONFIDENCE INTERVAL",
-          alignment: "left",
           width: 45,
-          loadingSkeletonWidth: SKELETON_WIDTH,
         },
         {
+          alignment: "left",
           id: "exponent",
           name: "EXPONENT",
-          alignment: "left",
           width: 8,
         },
         {
+          alignment: "left",
           id: "numPublishers",
           name: "# PUBLISHERS",
-          alignment: "left",
           width: 8,
         },
       ]}
+      fill
+      label="Price Feeds"
+      rounded
+      stickyHeader="appHeader"
       {...(props.isLoading
         ? {
             isLoading: true,
           }
         : {
-            rows: props.rows,
-            sortDescriptor: props.sortDescriptor,
-            onSortChange: props.onSortChange,
             emptyState: (
               <NoResults
-                query={props.search}
                 onClearSearch={() => {
                   props.onSearchChange("");
                 }}
+                query={props.search}
               />
             ),
+            onSortChange: props.onSortChange,
+            rows: props.rows,
+            sortDescriptor: props.sortDescriptor,
           })}
     />
   </Card>
```

### apps/insights/src/components/Publisher/price-feeds.module.scss
```diff
@@ -0,0 +1,3 @@
+.symbol {
+  flex-grow: 1;
+}
```

### apps/insights/src/components/Publisher/price-feeds.tsx
```diff
@@ -1,13 +1,13 @@
 import { SymbolPairTag } from "@pythnetwork/component-library/SymbolPairTag";
 import { notFound } from "next/navigation";
-
-import { getPriceFeeds } from "./get-price-feeds";
 import type { Cluster } from "../../services/pyth";
 import { parseCluster } from "../../services/pyth";
 import { AssetClassBadge } from "../AssetClassBadge";
 import type { PriceComponent } from "../PriceComponentsCard";
 import { PriceComponentsCard } from "../PriceComponentsCard";
 import { PriceFeedIcon } from "../PriceFeedIcon";
+import { getPriceFeeds } from "./get-price-feeds";
+import styles from "./price-feeds.module.scss";
 
 type Props = {
   params: Promise<{
@@ -30,31 +30,32 @@ export const PriceFeeds = async ({ params }: Props) => {
 
   return (
     <PriceFeedsCard
-      metricsTime={metricsTime}
-      publisherKey={key}
       cluster={parsedCluster}
+      metricsTime={metricsTime}
       priceFeeds={feeds.map(({ ranking, feed, status }) => ({
-        symbol: feed.symbol,
+        assetClass: feed.product.asset_type,
+        deviationScore: ranking?.deviation_score,
+        displaySymbol: feed.product.display_symbol,
+        feedKey: feed.product.price_account,
+        firstEvaluation: ranking?.first_ranking_time,
+        id: feed.product.price_account,
         name: (
           <SymbolPairTag
-            displaySymbol={feed.product.display_symbol}
+            className={styles.symbol}
             description={feed.product.description}
+            displaySymbol={feed.product.display_symbol}
             icon={<PriceFeedIcon assetClass={feed.product.asset_type} />}
           />
         ),
-        score: ranking?.final_score,
+        nameAsString: feed.product.display_symbol,
         rank: ranking?.final_rank,
-        uptimeScore: ranking?.uptime_score,
-        deviationScore: ranking?.deviation_score,
+        score: ranking?.final_score,
         stalledScore: ranking?.stalled_score,
         status,
-        feedKey: feed.product.price_account,
-        nameAsString: feed.product.display_symbol,
-        id: feed.product.price_account,
-        assetClass: feed.product.asset_type,
-        displaySymbol: feed.product.display_symbol,
-        firstEvaluation: ranking?.first_ranking_time,
+        symbol: feed.symbol,
+        uptimeScore: ranking?.uptime_score,
       }))}
+      publisherKey={key}
     />
   );
 };
@@ -73,29 +74,29 @@ type PriceFeedsCardProps =
 
 const PriceFeedsCard = (props: PriceFeedsCardProps) => (
   <PriceComponentsCard
-    label="Price Feeds"
-    searchPlaceholder="Feed symbol"
-    nameLoadingSkeleton={<SymbolPairTag isLoading />}
     extraColumns={[
       {
-        id: "assetClassBadge",
-        name: "ASSET CLASS",
         alignment: "left",
         allowsSorting: true,
+        id: "assetClassBadge",
+        name: "ASSET CLASS",
       },
     ]}
+    label="Price Feeds"
+    nameLoadingSkeleton={<SymbolPairTag isLoading />}
     nameWidth={90}
+    searchPlaceholder="Feed symbol"
     {...(props.isLoading
       ? { isLoading: true }
       : {
           metricsTime: props.metricsTime,
           priceComponents: props.priceFeeds.map((feed) => ({
             ...feed,
-            cluster: props.cluster,
-            publisherKey: props.publisherKey,
             assetClassBadge: (
               <AssetClassBadge>{feed.assetClass}</AssetClassBadge>
             ),
+            cluster: props.cluster,
+            publisherKey: props.publisherKey,
           })),
         })}
   />
```

### apps/insights/src/components/Publisher/top-feeds-table.module.scss
```diff
@@ -6,6 +6,10 @@
   }
 }
 
+.symbol {
+  flex-grow: 1;
+}
+
 .table {
   display: none;
 
```

### apps/insights/src/components/Publisher/top-feeds-table.tsx
```diff
@@ -6,13 +6,12 @@ import type { RowConfig } from "@pythnetwork/component-library/Table";
 import { Table } from "@pythnetwork/component-library/Table";
 import type { ReactNode } from "react";
 import { useMemo } from "react";
-
-import styles from "./top-feeds-table.module.scss";
 import type { Cluster } from "../../services/pyth";
 import type { Status } from "../../status";
 import { AssetClassBadge } from "../AssetClassBadge";
 import { usePriceComponentDrawer } from "../PriceComponentDrawer";
 import { Score } from "../Score";
+import styles from "./top-feeds-table.module.scss";
 
 type Props =
   | LoadingTopFeedsTableImplProps
@@ -52,16 +51,17 @@ const ResolvedTopFeedsTable = ({
   const drawerComponents = useMemo(
     () =>
       feeds.map((feed) => ({
+        cluster,
+        feedKey: feed.key,
         name: (
           <SymbolPairTag
-            displaySymbol={feed.displaySymbol}
+            className={styles.symbol}
             description={feed.description}
+            displaySymbol={feed.displaySymbol}
             icon={feed.icon}
           />
         ),
         publisherKey,
-        feedKey: feed.key,
-        cluster,
         ...feed,
       })),
     [feeds, cluster, publisherKey],
@@ -74,17 +74,17 @@ const ResolvedTopFeedsTable = ({
   const rows = useMemo(
     () =>
       drawerComponents.map((feed) => ({
-        id: feed.symbol,
-        textValue: feed.symbol,
-        header: feed.name,
         data: {
           asset: feed.name,
           assetClass: <AssetClassBadge>{feed.assetClass}</AssetClassBadge>,
-          score: <Score width={props.publisherScoreWidth} score={feed.score} />,
+          score: <Score score={feed.score} width={props.publisherScoreWidth} />,
         },
+        header: feed.name,
+        id: feed.symbol,
         onAction: () => {
           selectComponent(feed);
         },
+        textValue: feed.symbol,
       })),
     [drawerComponents, props.publisherScoreWidth, selectComponent],
   );
@@ -119,41 +119,41 @@ const TopFeedsTableImpl = ({
 }: TopFeedsTableImplProps) => (
   <>
     <EntityList
-      label={label}
       className={styles.list ?? ""}
-      headerLoadingSkeleton={nameLoadingSkeleton}
       fields={[
         { id: "score", name: "Score" },
         { id: "assetClass", name: "Asset Class" },
       ]}
+      headerLoadingSkeleton={nameLoadingSkeleton}
+      label={label}
       {...(props.isLoading ? { isLoading: true } : { rows: props.rows })}
     />
     <Table
-      label={label}
-      rounded
-      fill
       className={styles.table ?? ""}
       columns={[
         {
+          alignment: "left",
           id: "score",
           name: "SCORE",
-          alignment: "left",
           width: publisherScoreWidth,
         },
         {
+          alignment: "left",
           id: "asset",
-          name: "ASSET",
           isRowHeader: true,
-          alignment: "left",
           loadingSkeleton: nameLoadingSkeleton,
+          name: "ASSET",
         },
         {
+          alignment: "right",
           id: "assetClass",
           name: "ASSET CLASS",
-          alignment: "right",
           width: 40,
         },
       ]}
+      fill
+      label={label}
+      rounded
       {...(props.isLoading ? { isLoading: true } : { rows: props.rows })}
     />
   </>
```

### packages/component-library/src/SymbolPairTag/index.module.scss
```diff
@@ -50,18 +50,11 @@
 
     .description {
       color: theme.color("muted");
-      overflow: initial;
+      overflow: hidden;
       text-overflow: ellipsis;
-      white-space: normal;
+      white-space: unset;
 
       @include theme.text("xs", "medium");
-
-      // reset the above on large devices, to match when the price feeds grid switches over
-      @include theme.breakpoint("2xl") {
-        overflow: hidden;
-        text-overflow: ellipsis;
-        white-space: unset;
-      }
     }
   }
 
```

### packages/component-library/src/useDrawer/index.module.scss
```diff
@@ -104,6 +104,7 @@
         display: flex;
         flex-flow: row nowrap;
         gap: theme.spacing(3);
+        flex-grow: 1;
       }
 
       .headingEnd {
```

### pnpm-workspace.yaml
```diff
@@ -182,7 +182,7 @@ catalog:
   type-fest: ^5.2.0
   typedoc: ^0.26.8
   typescript: ^5.9.3
-  vercel: ^41.4.1
+  vercel: ^50.32.4
   viem: ^2.39.0
   wagmi: ^2.14.16
   yargs: ^18.0.0
```
