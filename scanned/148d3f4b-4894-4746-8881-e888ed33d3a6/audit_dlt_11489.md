# [?] truncate EVM addresses + add status legend, fix overflow

## Summary
Severity: Unknown
Chain: Oracle
Component: pyth-network/pyth-crosschain
Published: 2026-05-25
Source: https://github.com/pyth-network/pyth-crosschain/commit/3b681a3c2c8727b6ba222bb6ef530b3ce26dbf35
Type: security-commit

## Details
truncate EVM addresses + add status legend, fix overflow

- Wrap the EVM status table in an overflow-x container so wide rows do
  not bleed into the sidebar on narrow viewports.
- Pass maxLength={6} to CopyAddress so addresses render as
  "0x2880...C17B43" with the copy icon + explorer link still using the
  full address; eliminates the need for horizontal scrolling at typical
  reading widths.
- Add a small legend above each table: green swatch = "Upgraded", red
  swatch = "Will be dropped", so readers can decode the row tint at a
  glance.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### apps/developer-hub/src/components/EvmContractsStatusTable/index.tsx
```diff
@@ -89,10 +89,11 @@ const renderAddress = (address: string, explorer?: string) =>
   explorer ? (
     <CopyAddress
       address={address}
+      maxLength={6}
       url={`${explorer.replace(/\/$/, "")}/address/${address}`}
     />
   ) : (
-    <CopyAddress address={address} />
+    <CopyAddress address={address} maxLength={6} />
   );
 
 const EvmContractsStatusTable = async ({
@@ -112,34 +113,54 @@ const EvmContractsStatusTable = async ({
   }
 
   return (
-    <table>
-      <thead>
-        <tr>
-          <th>Network</th>
-          <th>Current Address</th>
-          <th>Upgraded Address</th>
-        </tr>
-      </thead>
-      <tbody>
-        {statuses.map((s) => {
-          const isUpgraded = s.upgradedAddress !== null;
-          const bgClass = isUpgraded
-            ? "bg-green-50 dark:bg-green-950/30"
-            : "bg-red-50 dark:bg-red-950/30";
-          return (
-            <tr key={s.chainId} className={bgClass}>
-              <td>{s.name}</td>
-              <td>{renderAddress(s.currentAddress, s.explorer)}</td>
-              <td>
-                {isUpgraded && s.upgradedAddress !== null
-                  ? renderAddress(s.upgradedAddress, s.explorer)
-                  : null}
-              </td>
-            </tr>
-          );
-        })}
-      </tbody>
-    </table>
+    <>
+      <div className="flex gap-4 text-sm my-2">
+        <span className="inline-flex items-center gap-2">
+          <span
+            aria-hidden
+            className="inline-block w-3 h-3 rounded-sm border bg-green-50 dark:bg-green-950/30"
+          />
+          Upgraded
+        </span>
+        <span className="inline-flex items-center gap-2">
+          <span
+            aria-hidden
+            className="inline-block w-3 h-3 rounded-sm border bg-red-50 dark:bg-red-950/30"
+          />
+          Will be dropped
+        </span>
+      </div>
+      <div className="overflow-x-auto">
+        <table>
+          <thead>
+          <tr>
+            <th>Network</th>
+            <th>Current Address</th>
+            <th>Upgraded Address</th>
+          </tr>
+        </thead>
+        <tbody>
+          {statuses.map((s) => {
+            const isUpgraded = s.upgradedAddress !== null;
+            const bgClass = isUpgraded
+              ? "bg-green-50 dark:bg-green-950/30"
+              : "bg-red-50 dark:bg-red-950/30";
+            return (
+              <tr key={s.chainId} className={bgClass}>
+                <td>{s.name}</td>
+                <td>{renderAddress(s.currentAddress, s.explorer)}</td>
+                <td>
+                  {isUpgraded && s.upgradedAddress !== null
+                    ? renderAddress(s.upgradedAddress, s.explorer)
+                    : null}
+                </td>
+              </tr>
+            );
+          })}
+        </tbody>
+      </table>
+    </div>
+    </>
   );
 };
 
```
