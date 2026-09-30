# [?] fix: hidden overflowX and min/max width for images

## Summary
Severity: Unknown
Chain: ZK
Component: semaphore-protocol/semaphore
Published: 2023-12-11
Source: https://github.com/semaphore-protocol/semaphore/commit/ff4a739426e7b269ba5a3aca0aa54198f9ac6e74
Type: security-commit

## Details
fix: hidden overflowX and min/max width for images

Former-commit-id: 395f3bd8c52e887fc0d29992c9bb209de5e10769

## Patch
### apps/website/src/app/page.tsx
```diff
@@ -27,7 +27,8 @@ export default function Home() {
                         alt="Midnight whispers image"
                         src="https://semaphore.cedoor.dev/midnight-whispers.jpg"
                         objectFit="cover"
-                        w="full"
+                        minWidth="100%"
+                        maxWidth="100%"
                         h="full"
                     />
                 </Box>
@@ -202,7 +203,8 @@ export default function Home() {
                         alt="Fluttering shadow image"
                         src="https://semaphore.cedoor.dev/shadow-flutter.jpg"
                         objectFit="cover"
-                        w="full"
+                        minWidth="100%"
+                        maxWidth="100%"
                         h="full"
                     />
                 </Box>
```

### apps/website/src/styles/styles.ts
```diff
@@ -11,7 +11,8 @@ const styles: Styles = {
             color: "white"
         },
         "body, #__next": {
-            minHeight: "100vh"
+            minHeight: "100vh",
+            overflowX: "hidden"
         },
         "#__next": {
             display: "flex",
```
