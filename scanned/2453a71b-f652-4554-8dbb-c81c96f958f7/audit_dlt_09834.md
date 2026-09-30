# [?] add staking transaction unit test for tx copy; fix panic error

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-11-19
Source: https://github.com/harmony-one/harmony/commit/2586f16899981bc6a503da6762e0a40cf8b4c6b1
Type: security-commit

## Details
add staking transaction unit test for tx copy; fix panic error

## Patch
### staking/types/transaction.go
```diff
@@ -4,7 +4,6 @@ import (
 	"errors"
 	"io"
 	"math/big"
-	"reflect"
 	"sync/atomic"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -35,7 +34,7 @@ func (d *txdata) CopyFrom(d2 *txdata) {
 	d.AccountNonce = d2.AccountNonce
 	d.Price = new(big.Int).Set(d2.Price)
 	d.GasLimit = d2.GasLimit
-	d.StakeMsg = reflect.New(reflect.ValueOf(d2.StakeMsg).Elem().Type()).Interface()
+	d.StakeMsg = d2.StakeMsg
 	d.V = new(big.Int).Set(d2.V)
 	d.R = new(big.Int).Set(d2.R)
 	d.S = new(big.Int).Set(d2.S)
```

### staking/types/transaction_test.go
```diff
@@ -0,0 +1,90 @@
+package types
+
+import (
+	"math/big"
+	"testing"
+
+	"github.com/ethereum/go-ethereum/common"
+	"github.com/harmony-one/bls/ffi/go/bls"
+	common2 "github.com/harmony-one/harmony/internal/common"
+	numeric "github.com/harmony-one/harmony/numeric"
+	"github.com/harmony-one/harmony/shard"
+)
+
+// for testing purpose
+var (
+	testAccount    = "one1pdv9lrdwl0rg5vglh4xtyrv3wjk3wsqket7zxy"
+	testBLSPubKey  = "65f55eb3052f9e9f632b2923be594ba77c55543f5c58ee1454b9cfd658d25e06373b0f7d42a19c84768139ea294f6204"
+	testBLSPubKey2 = "40379eed79ed82bebfb4310894fd33b6a3f8413a78dc4d43b98d0adc9ef69f3285df05eaab9f2ce5f7227f8cb920e809"
+)
+
+func CreateTestNewTransaction() (*StakingTransaction, error) {
+	dAddr, _ := common2.Bech32ToAddress(testAccount)
+
+	stakePayloadMaker := func() (Directive, interface{}) {
+		p := &bls.PublicKey{}
+		p.DeserializeHexStr(testBLSPubKey)
+		pub := shard.BlsPublicKey{}
+		pub.FromLibBLSPublicKey(p)
+
+		ra, _ := numeric.NewDecFromStr("0.7")
+		maxRate, _ := numeric.NewDecFromStr("1")
+		maxChangeRate, _ := numeric.NewDecFromStr("0.5")
+		return DirectiveCreateValidator, CreateValidator{
+			Description: &Description{
+				Name:            "SuperHero",
+				Identity:        "YouWouldNotKnow",
+				Website:         "Secret Website",
+				SecurityContact: "LicenseToKill",
+				Details:         "blah blah blah",
+			},
+			CommissionRates: CommissionRates{
+				Rate:          ra,
+				MaxRate:       maxRate,
+				MaxChangeRate: maxChangeRate,
+			},
+			MinSelfDelegation:  big.NewInt(10),
+			MaxTotalDelegation: big.NewInt(3000),
+			ValidatorAddress:   common.Address(dAddr),
+			SlotPubKeys:        []shard.BlsPublicKey{pub},
+			Amount:             big.NewInt(100),
+		}
+	}
+
+	gasPrice := big.NewInt(1)
+	return NewStakingTransaction(0, 600000, gasPrice, stakePayloadMaker)
+}
+
+func TestTransactionCopy(t *testing.T) {
+	tx1, err := CreateTestNewTransaction()
+	if err != nil {
+		t.Errorf("cannot create new staking transaction, %v\n", err)
+	}
+	tx2 := tx1.Copy()
+
+	cv1 := tx1.data.StakeMsg.(CreateValidator)
+	cv1.Amount = big.NewInt(20)
+	cv1.Description.Name = "NewName"
+
+	p := &bls.PublicKey{}
+	p.DeserializeHexStr(testBLSPubKey2)
+	pub := shard.BlsPublicKey{}
+	pub.FromLibBLSPublicKey(p)
+	cv1.SlotPubKeys = append(cv1.SlotPubKeys, pub)
+
+	tx1.data.StakeMsg = cv1
+
+	cv2 := tx2.data.StakeMsg.(CreateValidator)
+
+	if cv1.Amount.Cmp(cv2.Amount) == 0 {
+		t.Errorf("Amount should not be equal")
+	}
+
+	if len(cv1.SlotPubKeys) == len(cv2.SlotPubKeys) {
+		t.Errorf("SlotPubKeys should not be equal length")
+	}
+
+	if len(cv1.Description.Name) == len(cv2.Description.Name) {
+		t.Errorf("Description name should not be the same")
+	}
+}
```
