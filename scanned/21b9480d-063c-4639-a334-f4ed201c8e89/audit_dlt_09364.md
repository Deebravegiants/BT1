# [?] fix: handle error event on SSH agent socket to prevent Node crash (#22090)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-03-30
Source: https://github.com/AztecProtocol/aztec-packages/commit/49661c15095d89432afcdf8d9083565521b7c60a
Type: security-commit

## Details
fix: handle error event on SSH agent socket to prevent Node crash (#22090)

## Patch
### yarn-project/accounts/src/utils/ssh_agent.ts
```diff
@@ -41,6 +41,7 @@ type StoredKey = {
 export function getIdentities(): Promise<StoredKey[]> {
   return new Promise((resolve, reject) => {
     const stream = connectToAgent();
+    stream.on('error', reject);
     stream.on('connect', () => {
       const request = Buffer.concat([
         Buffer.from([0, 0, 0, 5 + 4]), // length
@@ -96,6 +97,7 @@ export function getIdentities(): Promise<StoredKey[]> {
 export function signWithAgent(keyType: Buffer, curveName: Buffer, publicKey: Buffer, data: Buffer) {
   return new Promise<Buffer>((resolve, reject) => {
     const stream = connectToAgent();
+    stream.on('error', reject);
     stream.on('connect', () => {
       // Construct the key blob
       const keyBlob = Buffer.concat([
```
