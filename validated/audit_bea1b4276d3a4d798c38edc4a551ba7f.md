### No vulnerability found for this question.

**Analysis supporting this conclusion:**

`validateBchAddress` in `packages/intents-sdk/src/lib/validateAddress.ts` deliberately accepts legacy base58check addresses (`1...`/`3...`) as valid BCH destinations, per the function's own doc comment: "Legacy addresses (1... for P2PKH, 3... for P2SH) - shared with Bitcoin".
<cite repo="Alyssadaypin/sdk-monorepo--001" path="packages/intents-sdk/src/lib/validateAddress.ts" start="204="225" />

This is not a validation gap but a reflection of Bitcoin Cash's actual history: BCH forked from BTC and, prior to the 2018 CashAddr rollout, used (and still accepts) the identical base58check P2PKH/P2SH address format and hash160 payload as Bitcoin. A `1...`/`3...` string decodes to the same script hash on both chains, and it is spendable by whoever holds the private key for that hash160 — on **either** network. The physical settlement network is determined by the bridge/asset chosen (`nep141:bch.omft.near` routes through the BCH withdrawal path), not by the format of the address string. So `WITHDRAW_TO:<legacyAddr>` sent through the BCH bridge results in an actual BCH-network transaction to a script the same keyholder controls — there is no "(chain=Bitcoin, address)" divergent payment; the transaction never touches the Bitcoin network at all.

The existing test suite validates this exact design intent, explicitly asserting that legacy `1.../3...` addresses are accepted as valid BCH addresses. [1](#0-0) 

`createWithdrawMemo` only strips a `bitcoincash:` prefix when present and otherwise passes the address through unchanged, which is correct because legacy-format addresses require no prefix stripping to remain valid BCH withdrawal targets. [2](#0-1) 

Note: the question cites `packages/intents-sdk/src/bridges/omni-bridge/error.ts` as the file scope, but the actual `validateBchAddress`/`createWithdrawMemo` logic lives in `packages/intents-sdk/src/lib/validateAddress.ts` and `packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts` — no such logic exists in `omni-bridge/error.ts`.

Because the underlying UTXO script/key is shared between BTC and BCH for these legacy addresses, there is no fund misdelivery to an unintended party — the claimed equality break does not materialize.

### Citations

**File:** packages/intents-sdk/src/lib/validateAddress.spec.ts (L758-782)
```typescript
describe("validateBchAddress()", () => {
	it("accepts valid addresses", () => {
		const list = [
			// Legacy P2PKH (1...)
			"1BpEi6DfDAUFd7GtittLSdBeYJvcoaVggu",
			"1KXrWXciRDZUpQwQmuM1DbwsKDLYAYsVLR",
			// Legacy P2SH (3...)
			"3CWFddi6m4ndiGyKqzYvsFYagqDLPVMTzC",
			"3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
			// CashAddr P2PKH (q...) - 160-bit hash, 42 chars
			"qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a",
			"bitcoincash:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a",
			"qp3wjpa3tjlj042z2wv7hahsldgwhwy0rq9sywjpyy",
			// CashAddr P2SH (p...) - 160-bit hash, 42 chars
			"pp8skudq3x5hzw8ew7vzsw8tn4k8wxsqsv0lt0mf3g",
			"bitcoincash:pp8skudq3x5hzw8ew7vzsw8tn4k8wxsqsv0lt0mf3g",
			// CashAddr 256-bit hash (61 chars) - from official spec test vectors
			"qvch8mmxy0rtfrlarg7ucrxxfzds5pamg73h7370aa87d80gyhqxq5nlegake",
			"bitcoincash:qvch8mmxy0rtfrlarg7ucrxxfzds5pamg73h7370aa87d80gyhqxq5nlegake",
		];

		for (const address of list) {
			expect(validateBchAddress(address)).toBe(true);
		}
	});
```

**File:** packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts (L28-49)
```typescript
function createWithdrawMemo({
	receiverAddress,
	xrpMemo,
}: {
	receiverAddress: string;
	xrpMemo: string | undefined;
}) {
	// Strip "bitcoincash:" prefix from BCH CashAddr addresses
	const normalizedAddress = receiverAddress
		.toLowerCase()
		.startsWith("bitcoincash:")
		? receiverAddress.slice("bitcoincash:".length)
		: receiverAddress;

	const memo = ["WITHDRAW_TO", normalizedAddress];

	if (xrpMemo != null && xrpMemo !== "") {
		memo.push(xrpMemo);
	}

	return memo.join(":");
}
```
