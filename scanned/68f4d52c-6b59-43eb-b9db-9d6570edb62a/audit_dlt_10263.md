# [?] fix: overflow issue of chain selector modal (#444)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2022-01-06
Source: https://github.com/RabbyHub/Rabby/commit/8f24cf7bb86f6a22caf63931b88b6e15d976b353
Type: security-commit

## Details
fix: overflow issue of chain selector modal (#444)

## Patch
### src/ui/component/ChainCard/index.tsx
```diff
@@ -15,13 +15,15 @@ const ChainCard = ({
   saveToPin,
   removeFromPin,
   className,
+  onClick,
 }: {
   plus: boolean;
   showIcon: boolean;
   chain?: Chain;
   saveToPin?(chain: string): void;
   removeFromPin?(chain: string): void;
   className?: string;
+  onClick?(): void;
 }) => {
   const [isHovering, hoverProps] = useHover();
 
@@ -60,6 +62,7 @@ const ChainCard = ({
       ref={setNodeRef}
       {...attributes}
       style={style}
+      onClick={onClick}
     >
       {!plus ? (
         <div className={clsx('chain-card', 'cursor-pointer')} {...listeners}>
```

### src/ui/component/ChainSelector/Modal.tsx
```diff
@@ -94,22 +94,20 @@ const ChainSelectorModal = ({
         {savedChainsData.length > 0 && (
           <ul className="chain-selector-options">
             {savedChainsData.map((chain) => (
-              <div onClick={() => handleChange(chain.enum as CHAINS_ENUM)}>
-                <ChainCard
-                  chain={chain}
-                  key={chain.id}
-                  showIcon={false}
-                  plus={false}
-                  className="w-[176px] h-[56px]"
-                />
-              </div>
+              <ChainCard
+                chain={chain}
+                key={chain.id}
+                showIcon={false}
+                plus={false}
+                className="w-[176px] h-[56px]"
+                onClick={() => handleChange(chain.enum as CHAINS_ENUM)}
+              />
             ))}
           </ul>
         )}
-        <div
-          className="all-chais"
-          onClick={goToChainManagement}
-        >{`All chains >`}</div>
+        <div className="all-chais" onClick={goToChainManagement}>
+          {'All chains >'}
+        </div>
       </>
     </Drawer>
   );
```

### src/ui/component/ChainSelector/style.less
```diff
@@ -32,7 +32,7 @@
 }
 
 .chain-selector-options {
-  width: 400px;
+  width: 100%;
   max-height: 376px;
   display: flex;
   flex-wrap: wrap;
```
