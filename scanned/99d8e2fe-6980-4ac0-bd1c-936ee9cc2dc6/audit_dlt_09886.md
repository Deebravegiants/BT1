# [?] [staking] fix ToEthTx() panic (#3910)

## Summary
Severity: Unknown
Chain: IoTeX
Component: iotexproject/iotex-core
Published: 2023-08-01
Source: https://github.com/iotexproject/iotex-core/commit/2e02ec7f3d6b97b3596b4abb4bb6e4e703e5193a
Type: security-commit

## Details
[staking] fix ToEthTx() panic (#3910)

## Patch
### action/candidate_register.go
```diff
@@ -304,14 +304,20 @@ func (cr *CandidateRegister) EncodeABIBinary() ([]byte, error) {
 }
 
 func (cr *CandidateRegister) encodeABIBinary() ([]byte, error) {
-	operatorEthAddr := common.BytesToAddress(cr.operatorAddress.Bytes())
-	rewardEthAddr := common.BytesToAddress(cr.rewardAddress.Bytes())
-	ownerEthAddr := common.BytesToAddress(cr.ownerAddress.Bytes())
+	if cr.operatorAddress == nil {
+		return nil, ErrAddress
+	}
+	if cr.rewardAddress == nil {
+		return nil, ErrAddress
+	}
+	if cr.ownerAddress == nil {
+		return nil, ErrAddress
+	}
 	data, err := _candidateRegisterMethod.Inputs.Pack(
 		cr.name,
-		operatorEthAddr,
-		rewardEthAddr,
-		ownerEthAddr,
+		common.BytesToAddress(cr.operatorAddress.Bytes()),
+		common.BytesToAddress(cr.rewardAddress.Bytes()),
+		common.BytesToAddress(cr.ownerAddress.Bytes()),
 		cr.amount,
 		cr.duration,
 		cr.autoStake,
```

### action/candidate_update.go
```diff
@@ -200,9 +200,15 @@ func (cu *CandidateUpdate) EncodeABIBinary() ([]byte, error) {
 }
 
 func (cu *CandidateUpdate) encodeABIBinary() ([]byte, error) {
-	operatorEthAddr := common.BytesToAddress(cu.operatorAddress.Bytes())
-	rewardEthAddr := common.BytesToAddress(cu.rewardAddress.Bytes())
-	data, err := _candidateUpdateMethod.Inputs.Pack(cu.name, operatorEthAddr, rewardEthAddr)
+	if cu.operatorAddress == nil {
+		return nil, ErrAddress
+	}
+	if cu.rewardAddress == nil {
+		return nil, ErrAddress
+	}
+	data, err := _candidateUpdateMethod.Inputs.Pack(cu.name,
+		common.BytesToAddress(cu.operatorAddress.Bytes()),
+		common.BytesToAddress(cu.rewardAddress.Bytes()))
 	if err != nil {
 		return nil, err
 	}
```

### action/candidateregister_test.go
```diff
@@ -156,6 +156,16 @@ func TestCandidateRegisterABIEncodeAndDecode(t *testing.T) {
 	require.Equal(test.Duration, stake.Duration())
 	require.Equal(test.AutoStake, stake.AutoStake())
 	require.Equal(test.Payload, stake.Payload())
+
+	stake.ownerAddress = nil
+	_, err = stake.EncodeABIBinary()
+	require.Equal(ErrAddress, err)
+	stake.rewardAddress = nil
+	_, err = stake.EncodeABIBinary()
+	require.Equal(ErrAddress, err)
+	stake.operatorAddress = nil
+	_, err = stake.EncodeABIBinary()
+	require.Equal(ErrAddress, err)
 }
 
 func TestIsValidCandidateName(t *testing.T) {
```

### action/candidateupdate_test.go
```diff
@@ -90,4 +90,11 @@ func TestCandidateUpdateABIEncodeAndDecode(t *testing.T) {
 	require.Equal(_cuName, stake.Name())
 	require.Equal(_cuOperatorAddrStr, stake.OperatorAddress().String())
 	require.Equal(_cuRewardAddrStr, stake.RewardAddress().String())
+
+	stake.rewardAddress = nil
+	_, err = stake.EncodeABIBinary()
+	require.Equal(ErrAddress, err)
+	stake.operatorAddress = nil
+	_, err = stake.EncodeABIBinary()
+	require.Equal(ErrAddress, err)
 }
```

### pkg/recovery/recovery.go
```diff
@@ -12,9 +12,9 @@ import (
 	"runtime/pprof"
 	"time"
 
-	"github.com/shirou/gopsutil/v3/load"
 	"github.com/shirou/gopsutil/v3/cpu"
 	"github.com/shirou/gopsutil/v3/disk"
+	"github.com/shirou/gopsutil/v3/load"
 	"github.com/shirou/gopsutil/v3/mem"
 
 	"github.com/iotexproject/iotex-core/pkg/log"
```
