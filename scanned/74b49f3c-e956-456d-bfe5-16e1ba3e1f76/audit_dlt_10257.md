# [?] fix: overflow display of token in balance change (#2596)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2024-11-01
Source: https://github.com/RabbyHub/Rabby/commit/735a577041aee44516020ddaeb5de338bc151e33
Type: security-commit

## Details
fix: overflow display of token in balance change (#2596)

* fix: overflow display of token in balance change

* fix: style

## Patch
### src/ui/views/Approval/components/TxComponents/BalanceChange.tsx
```diff
@@ -279,23 +279,27 @@ const BalanceChange = ({
           )}
           {sendTokenList?.map((token) => (
             <Col className="py-10 items-center" key={token.id}>
-              <Row isTitle className="text-[16px] overflow-hidden">
+              <Row isTitle className="text-[16px]">
                 <LogoWithText
-                  className="overflow-hidden"
                   logoSize={24}
                   logo={token.logo_url}
                   text={
-                    <>
-                      <span className="text-red-forbidden font-medium">
+                    <div className="max-w-[200px] flex relative">
+                      <span
+                        className="text-red-forbidden font-medium flex-1 overflow-hidden overflow-ellipsis"
+                        title={token.amount.toString()}
+                      >
                         - {formatAmount(token.amount)}
-                      </span>{' '}
+                      </span>
+
                       <span
                         onClick={() => handleClickToken(token)}
-                        className="group-hover:underline cursor-pointer text-red-forbidden font-medium"
+                        title={getTokenSymbol(token)}
+                        className="group-hover:underline cursor-pointer text-red-forbidden font-medium overflow-hidden overflow-ellipsis max-w-[100px] ml-4"
                       >
                         {getTokenSymbol(token)}
                       </span>
-                    </>
+                    </div>
                   }
                   logoRadius="100%"
                   icon={
@@ -318,23 +322,26 @@ const BalanceChange = ({
           ))}
           {receiveTokenList?.map((token) => (
             <Col className="py-10 items-center" key={token.id}>
-              <Row isTitle className="text-[16px] overflow-hidden">
+              <Row isTitle className="text-[16px]">
                 <LogoWithText
-                  className="overflow-hidden"
                   logoSize={24}
                   logo={token.logo_url}
                   text={
-                    <>
-                      <span className="text-green font-medium">
+                    <div className="max-w-[200px] flex relative">
+                      <span
+                        className="text-green font-medium flex-1 overflow-hidden overflow-ellipsis"
+                        title={token.amount.toString()}
+                      >
                         + {formatAmount(token.amount)}
-                      </span>{' '}
+                      </span>
                       <span
                         onClick={() => handleClickToken(token)}
-                        className="group-hover:underline cursor-pointer text-green font-medium"
+                        title={getTokenSymbol(token)}
+                        className="group-hover:underline cursor-pointer text-green font-medium overflow-hidden overflow-ellipsis max-w-[80px] ml-2"
                       >
                         {getTokenSymbol(token)}
                       </span>
-                    </>
+                    </div>
                   }
                   logoRadius="100%"
                   icon={
```
