# [?] fix(x/accounts): check for overflows in multisig weights and votes (#20384)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-05-21
Source: https://github.com/cosmos/cosmos-sdk/commit/a2dd2a0923bf4f1ab0ca04178a3815d2d1dc8d52
Type: security-commit

## Details
fix(x/accounts): check for overflows in multisig weights and votes (#20384)

## Patch
### x/accounts/defaults/multisig/account.go
```diff
@@ -91,7 +91,10 @@ func (a *Account) Init(ctx context.Context, msg *v1.MsgInit) (*v1.MsgInitRespons
 			return nil, err
 		}
 
-		totalWeight += msg.Members[i].Weight
+		totalWeight, err = safeAdd(totalWeight, msg.Members[i].Weight)
+		if err != nil {
+			return nil, err
+		}
 	}
 
 	if err := validateConfig(*msg.Config, totalWeight); err != nil {
@@ -279,6 +282,7 @@ func (a Account) ExecuteProposal(ctx context.Context, msg *v1.MsgExecuteProposal
 	}
 
 	totalWeight := yesVotes + noVotes + abstainVotes
+
 	var (
 		rejectErr error
 		execErr   error
@@ -387,3 +391,14 @@ func (a *Account) RegisterQueryHandlers(builder *accountstd.QueryBuilder) {
 	accountstd.RegisterQueryHandler(builder, a.QueryProposal)
 	accountstd.RegisterQueryHandler(builder, a.QueryConfig)
 }
+
+func safeAdd(nums ...uint64) (uint64, error) {
+	var sum uint64
+	for _, num := range nums {
+		if sum+num < sum {
+			return 0, errors.New("overflow")
+		}
+		sum += num
+	}
+	return sum, nil
+}
```

### x/accounts/defaults/multisig/account_test.go
```diff
@@ -2,6 +2,7 @@ package multisig
 
 import (
 	"context"
+	"math"
 	"testing"
 	"time"
 
@@ -312,6 +313,29 @@ func TestUpdateConfig(t *testing.T) {
 				},
 			},
 		},
+		{
+			"change members, invalid weights",
+			&v1.MsgUpdateConfig{
+				UpdateMembers: []*v1.Member{
+					{
+						Address: "addr1",
+						Weight:  math.MaxUint64,
+					},
+					{
+						Address: "addr2",
+						Weight:  1,
+					},
+				},
+				Config: &v1.Config{
+					Threshold:    666,
+					Quorum:       400,
+					VotingPeriod: 60,
+				},
+			},
+			"overflow",
+			nil,
+			nil,
+		},
 	}
 
 	for _, tc := range testcases {
@@ -658,3 +682,33 @@ func TestProposalPassing(t *testing.T) {
 
 	require.Equal(t, expectedMembers, cfg.Members)
 }
+
+func TestWeightOverflow(t *testing.T) {
+	ctx, ss := newMockContext(t)
+	acc := setup(t, ctx, ss, nil)
+
+	startAcc := &v1.MsgInit{
+		Config: &v1.Config{
+			Threshold:    2640,
+			Quorum:       2000,
+			VotingPeriod: 60,
+		},
+		Members: []*v1.Member{
+			{
+				Address: "addr1",
+				Weight:  math.MaxUint64,
+			},
+		},
+	}
+
+	_, err := acc.Init(ctx, startAcc)
+	require.NoError(t, err)
+
+	// add another member with weight 1 to trigger an overflow
+	startAcc.Members = append(startAcc.Members, &v1.Member{
+		Address: "addr2",
+		Weight:  1,
+	})
+	_, err = acc.Init(ctx, startAcc)
+	require.ErrorContains(t, err, "overflow")
+}
```

### x/accounts/defaults/multisig/update_config.go
```diff
@@ -44,7 +44,11 @@ func (a Account) UpdateConfig(ctx context.Context, msg *v1.MsgUpdateConfig) (*v1
 	// get the weight from the stored members
 	totalWeight := uint64(0)
 	err := a.Members.Walk(ctx, nil, func(_ []byte, value uint64) (stop bool, err error) {
-		totalWeight += value
+		var adderr error
+		totalWeight, adderr = safeAdd(totalWeight, value)
+		if adderr != nil {
+			return true, adderr
+		}
 		return false, nil
 	})
 	if err != nil {
```
