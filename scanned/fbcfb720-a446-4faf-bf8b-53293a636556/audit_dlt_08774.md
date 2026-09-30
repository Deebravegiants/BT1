# [?] fix(security): address CVE-2026-23864 React Server Components DoS (#2157)

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2026-01-27
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/64c3bfebd7087cd584f4e4ad37f42e47d03e6dbf
Type: security-commit

## Details
fix(security): address CVE-2026-23864 React Server Components DoS (#2157)

## Patch
### bridge-ui/package.json
```diff
@@ -30,7 +30,7 @@
     "@layerswap/wallet-evm": "1.0.2",
     "@layerswap/widget": "1.0.5",
     "@lifi/widget": "3.23.3",
-    "@next/third-parties": "15.5.9",
+    "@next/third-parties": "15.5.10",
     "@solana/wallet-adapter-base": "0.9.26",
     "@solana/wallet-adapter-react": "0.15.38",
     "@solana/web3.js": "1.98.2",
@@ -44,10 +44,10 @@
     "gsap": "3.13.0",
     "loglevel": "1.9.2",
     "motion": "12.10.1",
-    "next": "15.5.9",
+    "next": "15.5.10",
     "pino-pretty": "13.0.0",
-    "react": "19.1.4",
-    "react-dom": "19.1.4",
+    "react": "19.1.5",
+    "react-dom": "19.1.5",
     "sharp": "0.33.5",
     "viem": "catalog:",
     "wagmi": "2.16.9",
```
