# [?] fix(ccip-server): prevent crash from malicious input to offchain-lookup-server (#8260)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2026-03-02
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/69b48fad510e773cdbc1c92c231790263b73b3ec
Type: security-commit

## Details
fix(ccip-server): prevent crash from malicious input to offchain-lookup-server (#8260)

## Patch
### .changeset/fix-offchain-lookup-crash.md
```diff
@@ -0,0 +1,6 @@
+---
+'@hyperlane-xyz/sdk': patch
+'@hyperlane-xyz/ccip-server': patch
+---
+
+The PostCallsSchema was tightened to validate `to` and `relayers` fields with ZHash regex, rejecting malicious input (empty strings, URLs, injection payloads) at parse time. A try/catch was added around `normalizeCalls` in `CallCommitmentsService` as defense-in-depth to return 400 instead of crashing the pod.
```

### .github/workflows/node-services-docker.yml
```diff
@@ -73,12 +73,14 @@ jobs:
           echo "TAG_SHA_DATE=${TAG_SHA}-${TAG_DATE}" >> $GITHUB_OUTPUT
 
           # Determine primary tag based on event type
+          # Replace forward slashes with dashes for Docker tag compatibility
+          SANITIZED_REF=$(echo '${{ github.ref_name }}' | tr '/' '-')
           if [ "${{ github.ref_type }}" = "tag" ]; then
-            echo "TAG=${{ github.ref_name }}" >> $GITHUB_OUTPUT
+            echo "TAG=${SANITIZED_REF}" >> $GITHUB_OUTPUT
           elif [ "${{ github.event_name }}" = "pull_request" ]; then
             echo "TAG=pr-${{ github.event.pull_request.number }}" >> $GITHUB_OUTPUT
           else
-            echo "TAG=${{ github.ref_name }}" >> $GITHUB_OUTPUT
+            echo "TAG=${SANITIZED_REF}" >> $GITHUB_OUTPUT
           fi
 
           # Determine platforms
```

### typescript/ccip-server/src/services/CallCommitmentsService.ts
```diff
@@ -80,10 +80,22 @@ export class CallCommitmentsService extends BaseService {
     const data = this.parseCommitmentBody(req.body, res, logger);
     if (!data) return;
 
-    const commitment = commitmentFromIcaCalls(
-      normalizeCalls(data.calls),
-      data.salt,
-    );
+    let commitment: string;
+    try {
+      commitment = commitmentFromIcaCalls(
+        normalizeCalls(data.calls),
+        data.salt,
+      );
+    } catch (error: unknown) {
+      logger.warn(
+        {
+          error: error instanceof Error ? error.message : error,
+          calls: data.calls,
+        },
+        'Invalid call data',
+      );
+      return res.status(400).json({ error: 'Invalid call data' });
+    }
     logger.setBindings({ commitment });
 
     logger.info(
```

### typescript/ccip-server/tests/services/CallCommitmentsService.test.ts
```diff
@@ -0,0 +1,64 @@
+import { describe, expect, jest, test } from '@jest/globals';
+
+import { commitmentFromIcaCalls, normalizeCalls } from '@hyperlane-xyz/sdk';
+
+import { CallCommitmentsService } from '../../src/services/CallCommitmentsService';
+
+function mockLogger() {
+  return {
+    info: jest.fn(),
+    warn: jest.fn(),
+    error: jest.fn(),
+    setBindings: jest.fn(),
+    child: jest.fn().mockReturnThis(),
+  };
+}
+
+function mockRes() {
+  const json = jest.fn();
+  const status = jest.fn().mockReturnValue({ json });
+  const sendStatus = jest.fn();
+  return { status, json, sendStatus };
+}
+
+describe('CallCommitmentsService.handleCommitment input validation', () => {
+  test('returns 400 when schema rejects invalid to address', async () => {
+    const logger = mockLogger();
+    const service = Object.create(CallCommitmentsService.prototype);
+    service.addLoggerServiceContext = () => logger;
+
+    const req = {
+      body: {
+        calls: [{ to: '', data: '0x', value: '0' }],
+        relayers: ['0x' + 'ab'.repeat(20)],
+        salt: '0x' + '00'.repeat(32),
+        commitmentDispatchTx: '0x' + 'ef'.repeat(32),
+        originDomain: 1,
+      },
+      log: logger,
+    };
+    const res = mockRes();
+
+    await service.handleCommitment(req, res);
+
+    expect(res.status).toHaveBeenCalledWith(400);
+    expect(res.json).toHaveBeenCalled();
+  });
+
+  test('normalizeCalls throws on malformed address that bypasses schema', () => {
+    expect(() => {
+      normalizeCalls([{ to: 'not-an-address', data: '0x', value: '0' }]);
+    }).toThrow('address bytes must not be empty');
+  });
+
+  test('commitmentFromIcaCalls works with valid normalized calls', () => {
+    const validAddress = '0x' + 'ab'.repeat(20);
+    const salt = '0x' + '00'.repeat(32);
+    const result = commitmentFromIcaCalls(
+      normalizeCalls([{ to: validAddress, data: '0x', value: '0' }]),
+      salt,
+    );
+    expect(result).toBeDefined();
+    expect(result.startsWith('0x')).toBe(true);
+  });
+});
```

### typescript/infra/helm/offchain-lookup-server/values-mainnet.yaml
```diff
@@ -6,7 +6,7 @@ image:
   # Modify this tag to deploy a new revision.
   # Images can be found here:
   # https://console.cloud.google.com/artifacts/docker/abacus-labs-dev/us/gcr.io/hyperlane-offchain-lookup-server
-  tag: ab078b0-20260127-171512
+  tag: fb4f9fe-20260302-224238
 
 # In Google Cloud Secret Manager, all secrets need to have a certain prefix in order to be accessible by
 # the Cluster Secret Store. For testnet this prefix is "hyperlane-testnet4"
```

### typescript/infra/helm/offchain-lookup-server/values-testnet.yaml
```diff
@@ -6,7 +6,7 @@ image:
   # Modify this tag to deploy a new revision.
   # Images can be found here:
   # https://console.cloud.google.com/artifacts/docker/abacus-labs-dev/us/gcr.io/hyperlane-offchain-lookup-server
-  tag: ab078b0-20260127-171512
+  tag: fb4f9fe-20260302-224238
 
 # In Google Cloud Secret Manager, all secrets need to have a certain prefix in order to be accessible by
 # the Cluster Secret Store. For testnet this prefix is "hyperlane-testnet4"
```

### typescript/infra/helm/offchain-lookup-server/values.yaml
```diff
@@ -6,7 +6,7 @@ image:
   # Modify this tag to deploy a new revision.
   # Images can be found here:
   # https://console.cloud.google.com/artifacts/docker/abacus-labs-dev/us/gcr.io/hyperlane-offchain-lookup-server
-  tag: ab078b0-20260127-171512
+  tag: fb4f9fe-20260302-224238
 
 secrets:
   name: 'offchain-lookup-server'
```

### typescript/sdk/src/middleware/account/InterchainAccount.test.ts
```diff
@@ -9,7 +9,81 @@ import { TestChainName } from '../../consts/testChains.js';
 import { MultiProvider } from '../../providers/MultiProvider.js';
 import { randomAddress } from '../../test/testUtils.js';
 
-import { InterchainAccount } from './InterchainAccount.js';
+import { InterchainAccount, PostCallsSchema } from './InterchainAccount.js';
+
+const validPayload = (overrides: Record<string, any> = {}) => ({
+  calls: [
+    {
+      to: '0x' + 'ab'.repeat(20),
+      data: '0x',
+      value: '0',
+    },
+  ],
+  relayers: ['0x' + 'cd'.repeat(20)],
+  salt: '0x' + '00'.repeat(32),
+  commitmentDispatchTx: '0x' + 'ef'.repeat(32),
+  originDomain: 1,
+  ...overrides,
+});
+
+describe('PostCallsSchema', () => {
+  it('accepts valid EVM address', () => {
+    const result = PostCallsSchema.safeParse(validPayload());
+    expect(result.success).to.be.true;
+  });
+
+  it('accepts valid bytes32 address', () => {
+    const result = PostCallsSchema.safeParse(
+      validPayload({
+        calls: [{ to: '0x' + 'ab'.repeat(32), data: '0x', value: '0' }],
+      }),
+    );
+    expect(result.success).to.be.true;
+  });
+
+  it('rejects empty string to address', () => {
+    const result = PostCallsSchema.safeParse(
+      validPayload({
+        calls: [{ to: '', data: '0x', value: '0' }],
+      }),
+    );
+    expect(result.success).to.be.false;
+  });
+
+  it('rejects URL as to address', () => {
+    const result = PostCallsSchema.safeParse(
+      validPayload({
+        calls: [{ to: 'http://evil.com', data: '0x', value: '0' }],
+      }),
+    );
+    expect(result.success).to.be.false;
+  });
+
+  it('rejects SQL injection in to address', () => {
+    const result = PostCallsSchema.safeParse(
+      validPayload({
+        calls: [{ to: "'; DROP TABLE--", data: '0x', value: '0' }],
+      }),
+    );
+    expect(result.success).to.be.false;
+  });
+
+  it('rejects prototype pollution in to address', () => {
+    const result = PostCallsSchema.safeParse(
+      validPayload({
+        calls: [{ to: '__proto__', data: '0x', value: '0' }],
+      }),
+    );
+    expect(result.success).to.be.false;
+  });
+
+  it('rejects invalid relayer address', () => {
+    const result = PostCallsSchema.safeParse(
+      validPayload({ relayers: ['not-an-address'] }),
+    );
+    expect(result.success).to.be.false;
+  });
+});
 
 describe('InterchainAccount.getCallRemote', () => {
   const defaultGasLimit = BigNumber.from(50_000);
```

### typescript/sdk/src/middleware/account/InterchainAccount.ts
```diff
@@ -1,6 +1,7 @@
 import { BigNumber, PopulatedTransaction, ethers, utils } from 'ethers';
 import { z } from 'zod';
 
+import { ZHash } from '../../metadata/customZodTypes.js';
 import {
   InterchainAccountRouter,
   InterchainAccountRouter__factory,
@@ -545,13 +546,13 @@ export const PostCallsSchema = z.object({
   calls: z
     .array(
       z.object({
-        to: z.string(),
+        to: ZHash,
         data: z.string(),
         value: z.string().optional(),
       }),
     )
     .min(1),
-  relayers: z.array(z.string()),
+  relayers: z.array(ZHash),
   salt: z.string(),
   commitmentDispatchTx: z.string(),
   originDomain: z.number(),
```
