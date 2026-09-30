# [?] Prevent dApp from crashing after expiry (#696)

## Summary
Severity: Unknown
Chain: UMA
Component: UMAprotocol/protocol
Published: 2019-09-13
Source: https://github.com/UMAprotocol/protocol/commit/705dd4c5dbb3d0474ac7d771e0f8c647f2260c2d
Type: security-commit

## Details
Prevent dApp from crashing after expiry (#696)

Signed-off-by: Matthew Rice <matthewcrice32@gmail.com>

## Patch
### .circleci/config.yml
```diff
@@ -171,8 +171,8 @@ jobs:
           command: $(npm bin)/truffle migrate --reset --network test
       - restore_cache:
           keys: 
-            - v2-dapp-dep-cache-{{ checksum "voter-dapp/package.json" }}-{{ checksum "sponsor-dapp-v2/package.json" }}
-            - v2-dapp-dep-cache-
+            - v3-dapp-dep-cache-{{ checksum "voter-dapp/package.json" }}-{{ checksum "sponsor-dapp-v2/package.json" }}
+            - v3-dapp-dep-cache-
       - run:
           name: Install Voter dApp Dependencies
           working_directory: ~/protocol/voter-dapp
@@ -182,7 +182,7 @@ jobs:
           working_directory: ~/protocol/sponsor-dapp-v2
           command: npm install
       - save_cache:
-          key: v2-dapp-dep-cache-{{ checksum "voter-dapp/package.json" }}-{{ checksum "sponsor-dapp-v2/package.json" }}
+          key: v3-dapp-dep-cache-{{ checksum "voter-dapp/package.json" }}-{{ checksum "sponsor-dapp-v2/package.json" }}
           paths:
             - voter-dapp/node_modules
             - sponsor-dapp-v2/node_modules
```

### sponsor-dapp-v2/src/components/common/ExpandBox.js
```diff
@@ -21,7 +21,9 @@ class ExpandBox extends Component {
     });
 
     const convertTimestamp = timestamp => {
-      if (timestamp === UINT_MAX) {
+      if (timestamp == null) {
+        return "--";
+      } else if (timestamp === UINT_MAX) {
         return "None";
       } else {
         return moment.unix(timestamp).format("YYYY-MM-DD, HH:MM:SS");
```

### sponsor-dapp-v2/src/views/ManagePositions.js
```diff
@@ -69,15 +69,19 @@ function useFinancialContractData(tokenAddress) {
   data.tokenValue = useCacheCall(tokenAddress, "calcTokenValue");
   data.shortMarginBalance = useCacheCall(tokenAddress, "calcShortMarginBalance");
   data.excessMargin = useCacheCall(tokenAddress, "calcExcessMargin");
-  // TODO(ptare): This may revert in certain cases (which are unlikely to come up now).
-  data.updatedUnderlyingPrice = useCacheCall(tokenAddress, "getUpdatedUnderlyingPrice");
+
+  const updatedUnderlyingPrice = useCacheCall(tokenAddress, "getUpdatedUnderlyingPrice");
+
+  // If the blockchain value === null, this means that the call reverted, so we just make its children null (to prevent access errors down the line).
+  data.updatedUnderlyingPrice =
+    updatedUnderlyingPrice !== null ? updatedUnderlyingPrice : { underlyingPrice: null, time: null };
 
   data.totalSupply = useCacheCall(tokenAddress, "totalSupply");
   data.tokenBalance = useCacheCall(tokenAddress, "balanceOf", account);
 
   data.priceFeedAddress = useCacheCall("Finder", "getImplementationAddress", web3.utils.utf8ToHex("PriceFeed"));
 
-  if (!Object.values(data).every(Boolean)) {
+  if (!Object.values(data).every(val => val !== undefined)) {
     return { ready: false };
   }
   data.ready = true;
@@ -94,15 +98,23 @@ function useFinancialContractData(tokenAddress) {
 
   const totalSupplyBn = toBN(data.totalSupply);
   data.tokenOwnershipPercentage = computeSafePercentage(data.tokenBalance, totalSupplyBn);
-  data.tokenOwnershipValue = toBN(data.tokenBalance)
-    .mul(toBN(data.tokenValue))
-    .div(scalingFactor);
-  const navBn = toBN(data.nav);
-  const shortMarginBalanceBn = toBN(data.shortMarginBalance);
-  data.totalHoldings = navBn.add(shortMarginBalanceBn);
-  data.collateralizationRatio = computeSafePercentage(data.totalHoldings, navBn);
-  data.minRequiredMargin = shortMarginBalanceBn.sub(toBN(data.excessMargin));
-  data.minCollateralizationPercentage = computeSafePercentage(data.minRequiredMargin.add(navBn), navBn);
+  data.totalHoldings = toBN(data.derivativeStorage.longBalance).add(toBN(data.derivativeStorage.shortBalance));
+
+  if (data.nav && data.shortMarginBalance && data.excessMargin && data.tokenValue) {
+    data.tokenOwnershipValue = toBN(data.tokenBalance)
+      .mul(toBN(data.tokenValue))
+      .div(scalingFactor);
+    const navBn = toBN(data.nav);
+    const shortMarginBalanceBn = toBN(data.shortMarginBalance);
+    data.collateralizationRatio = computeSafePercentage(data.totalHoldings, navBn);
+    data.minRequiredMargin = shortMarginBalanceBn.sub(toBN(data.excessMargin));
+    data.minCollateralizationPercentage = computeSafePercentage(data.minRequiredMargin.add(navBn), navBn);
+  } else {
+    data.tokenOwnershipValue = null;
+    data.collateralizationRatio = null;
+    data.minRequiredMargin = null;
+    data.minCollateralizationPercentage = null;
+  }
   const { stateText, stateColor } = getStateDescription(data.derivativeStorage);
   data.stateText = stateText;
   data.stateColor = stateColor;
@@ -143,7 +155,8 @@ function ManagePositions(props) {
     return <div>Loading data</div>;
   }
 
-  const format = createFormatFunction(web3, 4);
+  const formatValidValue = createFormatFunction(web3, 4);
+  const format = val => (val ? formatValidValue(val) : "--");
 
   return (
     <div className="wrapper">
@@ -295,13 +308,18 @@ function ManagePositions(props) {
 
                           <td>
                             <strong>
-                              {format(data.totalHoldings)} DAI ({data.collateralizationRatio.toString()}%)
+                              {format(data.totalHoldings)} DAI (
+                              {data.collateralizationRatio ? data.collateralizationRatio.toString() : "--"}%)
                             </strong>
                           </td>
 
                           <td>
                             <strong>
-                              (min. {data.minCollateralizationPercentage.toString()}% needed to avoid liquidation)
+                              (min.{" "}
+                              {data.minCollateralizationPercentage
+                                ? data.minCollateralizationPercentage.toString()
+                                : "--"}
+                              % needed to avoid liquidation)
                             </strong>
                           </td>
                         </tr>
```
