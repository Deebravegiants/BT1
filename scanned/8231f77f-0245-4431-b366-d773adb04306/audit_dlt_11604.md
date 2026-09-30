# [?] fix: Non-determinism in sorting finality providers in the voting power table (#180)

## Summary
Severity: Unknown
Chain: Babylon
Component: babylonlabs-io/babylon
Published: 2024-10-11
Source: https://github.com/babylonlabs-io/babylon/commit/58e13f06030e8e7c9853219df610ccf698202635
Type: security-commit

## Details
fix: Non-determinism in sorting finality providers in the voting power table (#180)

Non-determinism is caused due to not considering cases where both two
items are jailed or non-timestamped, and when voting power is equal.
This PR addressed this by determining the order in those cases by the
increasing order of btc pk hex.

## Patch
### CHANGELOG.md
```diff
@@ -39,6 +39,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
 
 ### Bug fixes
 
+* [#180](https://github.com/babylonlabs-io/babylon/pull/180) Non-determinism in
+  sorting finality providers in the voting power table
 * [#154](https://github.com/babylonlabs-io/babylon/pull/154) Fix "edit-finality-provider" cmd argument index
 
 ### Improvements
```

### x/btcstaking/types/btcstaking.go
```diff
@@ -60,6 +60,18 @@ func SortFinalityProvidersWithZeroedVotingPower(fps []*FinalityProviderDistInfo)
 			return true
 		}
 
+		iPkHex, jPkHex := fps[i].BtcPk.MarshalHex(), fps[j].BtcPk.MarshalHex()
+
+		if iShouldBeZeroed && jShouldBeZeroed {
+			// Both have zeroed voting power, compare BTC public keys
+			return iPkHex < jPkHex
+		}
+
+		// both voting power the same, compare BTC public keys
+		if fps[i].TotalVotingPower == fps[j].TotalVotingPower {
+			return iPkHex < jPkHex
+		}
+
 		return fps[i].TotalVotingPower > fps[j].TotalVotingPower
 	})
 }
```

### x/btcstaking/types/btcstaking_test.go
```diff
@@ -0,0 +1,150 @@
+package types_test
+
+import (
+	"math/rand"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	"github.com/babylonlabs-io/babylon/testutil/datagen"
+	bbn "github.com/babylonlabs-io/babylon/types"
+	"github.com/babylonlabs-io/babylon/x/btcstaking/types"
+)
+
+func TestSortFinalityProvidersWithZeroedVotingPower(t *testing.T) {
+	tests := []struct {
+		name     string
+		fps      []*types.FinalityProviderDistInfo
+		expected []*types.FinalityProviderDistInfo
+	}{
+		{
+			name: "Sort by voting power",
+			fps: []*types.FinalityProviderDistInfo{
+				{Addr: "fp1", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x03}},
+				{Addr: "fp2", TotalVotingPower: 200, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x02}},
+				{Addr: "fp3", TotalVotingPower: 150, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x01}},
+			},
+			expected: []*types.FinalityProviderDistInfo{
+				{Addr: "fp2", TotalVotingPower: 200, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x02}},
+				{Addr: "fp3", TotalVotingPower: 150, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x01}},
+				{Addr: "fp1", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x03}},
+			},
+		},
+		{
+			name: "Jailed and non-timestamped providers at the end",
+			fps: []*types.FinalityProviderDistInfo{
+				{Addr: "fp1", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x04}},
+				{Addr: "fp2", TotalVotingPower: 200, IsJailed: true, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x02}},
+				{Addr: "fp3", TotalVotingPower: 150, IsJailed: false, IsTimestamped: false, BtcPk: &bbn.BIP340PubKey{0x03}},
+				{Addr: "fp4", TotalVotingPower: 50, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x01}},
+			},
+			expected: []*types.FinalityProviderDistInfo{
+				{Addr: "fp1", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x04}},
+				{Addr: "fp4", TotalVotingPower: 50, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x01}},
+				{Addr: "fp2", TotalVotingPower: 200, IsJailed: true, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x02}},
+				{Addr: "fp3", TotalVotingPower: 150, IsJailed: false, IsTimestamped: false, BtcPk: &bbn.BIP340PubKey{0x03}},
+			},
+		},
+		{
+			name: "Equal voting power, sort by BTC public key",
+			fps: []*types.FinalityProviderDistInfo{
+				{Addr: "fp1", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x03}},
+				{Addr: "fp2", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x01}},
+				{Addr: "fp3", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x02}},
+			},
+			expected: []*types.FinalityProviderDistInfo{
+				{Addr: "fp2", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x01}},
+				{Addr: "fp3", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x02}},
+				{Addr: "fp1", TotalVotingPower: 100, IsJailed: false, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x03}},
+			},
+		},
+		{
+			name: "Zeroed voting power, sort by BTC public key",
+			fps: []*types.FinalityProviderDistInfo{
+				{Addr: "fp1", TotalVotingPower: 200, IsJailed: true, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x03}},
+				{Addr: "fp2", TotalVotingPower: 150, IsJailed: false, IsTimestamped: false, BtcPk: &bbn.BIP340PubKey{0x01}},
+				{Addr: "fp3", TotalVotingPower: 100, IsJailed: true, IsTimestamped: false, BtcPk: &bbn.BIP340PubKey{0x02}},
+			},
+			expected: []*types.FinalityProviderDistInfo{
+				{Addr: "fp2", TotalVotingPower: 150, IsJailed: false, IsTimestamped: false, BtcPk: &bbn.BIP340PubKey{0x01}},
+				{Addr: "fp3", TotalVotingPower: 100, IsJailed: true, IsTimestamped: false, BtcPk: &bbn.BIP340PubKey{0x02}},
+				{Addr: "fp1", TotalVotingPower: 200, IsJailed: true, IsTimestamped: true, BtcPk: &bbn.BIP340PubKey{0x03}},
+			},
+		},
+	}
+
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			types.SortFinalityProvidersWithZeroedVotingPower(tt.fps)
+			require.Equal(t, tt.expected, tt.fps, "Sorted slice should match expected order")
+		})
+	}
+}
+
+// FuzzSortingDeterminism tests the property of the sorting algorithm that the result should
+// be deterministic
+func FuzzSortingDeterminism(f *testing.F) {
+	datagen.AddRandomSeedsToFuzzer(f, 1000)
+	f.Fuzz(func(t *testing.T, seed int64) {
+		r := rand.New(rand.NewSource(seed))
+		max_vp := 10000
+
+		vp0 := datagen.RandomInt(r, max_vp) + 10
+		vp1 := vp0 // this is for the case voting power is the same
+		vp2 := datagen.RandomInt(r, max_vp) + 10
+		vp3 := datagen.RandomInt(r, max_vp) + 10
+		vp4 := datagen.RandomInt(r, max_vp) + 10
+
+		pk1, err := datagen.GenRandomBIP340PubKey(r)
+		require.NoError(t, err)
+		pk2, err := datagen.GenRandomBIP340PubKey(r)
+		require.NoError(t, err)
+		pk3, err := datagen.GenRandomBIP340PubKey(r)
+		require.NoError(t, err)
+		pk4, err := datagen.GenRandomBIP340PubKey(r)
+		require.NoError(t, err)
+		pk5, err := datagen.GenRandomBIP340PubKey(r)
+		require.NoError(t, err)
+
+		fpsWithMeta := []*types.FinalityProviderDistInfo{
+			{TotalVotingPower: vp0, IsJailed: false, IsTimestamped: true, Addr: "addr0", BtcPk: pk1},
+			{TotalVotingPower: vp1, IsJailed: false, IsTimestamped: true, Addr: "addr1", BtcPk: pk2},
+			{TotalVotingPower: vp2, IsJailed: false, IsTimestamped: true, Addr: "addr2", BtcPk: pk3},
+			{TotalVotingPower: vp3, IsJailed: false, IsTimestamped: true, Addr: "addr3", BtcPk: pk4},
+			{TotalVotingPower: vp4, IsJailed: false, IsTimestamped: true, Addr: "addr4", BtcPk: pk5},
+		}
+		jailedIdx := datagen.RandomInt(r, len(fpsWithMeta))
+		noTimestampedIdx := datagen.RandomIntOtherThan(r, int(jailedIdx), len(fpsWithMeta))
+
+		fpsWithMeta[jailedIdx].IsJailed = true
+		fpsWithMeta[jailedIdx].IsTimestamped = false
+		fpsWithMeta[noTimestampedIdx].IsJailed = false
+		fpsWithMeta[noTimestampedIdx].IsTimestamped = false
+
+		fpsWithMeta1 := []*types.FinalityProviderDistInfo{
+			{TotalVotingPower: vp0, IsJailed: false, IsTimestamped: true, Addr: "addr0", BtcPk: pk1},
+			{TotalVotingPower: vp1, IsJailed: false, IsTimestamped: true, Addr: "addr1", BtcPk: pk2},
+			{TotalVotingPower: vp2, IsJailed: false, IsTimestamped: true, Addr: "addr2", BtcPk: pk3},
+			{TotalVotingPower: vp3, IsJailed: false, IsTimestamped: true, Addr: "addr3", BtcPk: pk4},
+			{TotalVotingPower: vp4, IsJailed: false, IsTimestamped: true, Addr: "addr4", BtcPk: pk5},
+		}
+
+		fpsWithMeta1[jailedIdx].IsJailed = true
+		fpsWithMeta1[jailedIdx].IsTimestamped = false
+		fpsWithMeta1[noTimestampedIdx].IsJailed = false
+		fpsWithMeta1[noTimestampedIdx].IsTimestamped = false
+
+		// Shuffle the fpsWithMeta1 slice
+		r.Shuffle(len(fpsWithMeta1), func(i, j int) {
+			fpsWithMeta1[i], fpsWithMeta1[j] = fpsWithMeta1[j], fpsWithMeta1[i]
+		})
+
+		types.SortFinalityProvidersWithZeroedVotingPower(fpsWithMeta)
+		types.SortFinalityProvidersWithZeroedVotingPower(fpsWithMeta1)
+
+		for i := 0; i < len(fpsWithMeta); i++ {
+			// our lists should be sorted in same order
+			require.Equal(t, fpsWithMeta[i].BtcPk.MarshalHex(), fpsWithMeta1[i].BtcPk.MarshalHex())
+		}
+	})
+}
```
