# [?] Fix potential panic with nil *big.Int (#7874)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2020-11-20
Source: https://github.com/OffchainLabs/prysm/commit/c3fc40907dddb9e9712ba7d7637c673fa689ee78
Type: security-commit

## Details
Fix potential panic with nil *big.Int (#7874)

* Fix potential panic with nil \*big.Int

* regression test

Co-authored-by: prylabs-bulldozer[bot] <58059840+prylabs-bulldozer[bot]@users.noreply.github.com>

## Patch
### beacon-chain/powchain/block_cache.go
```diff
@@ -45,12 +45,17 @@ type headerInfo struct {
 	Time   uint64
 }
 
-func headerToHeaderInfo(hdr *gethTypes.Header) *headerInfo {
+func headerToHeaderInfo(hdr *gethTypes.Header) (*headerInfo, error) {
+	if hdr.Number == nil {
+		// A nil number will panic when calling *big.Int.Set(...)
+		return nil, errors.New("cannot convert block header with nil block number")
+	}
+
 	return &headerInfo{
 		Hash:   hdr.Hash(),
 		Number: new(big.Int).Set(hdr.Number),
 		Time:   hdr.Time,
-	}
+	}, nil
 }
 
 // hashKeyFn takes the hex string representation as the key for a headerInfo.
@@ -151,7 +156,10 @@ func (b *headerCache) AddHeader(hdr *gethTypes.Header) error {
 	b.lock.Lock()
 	defer b.lock.Unlock()
 
-	hInfo := headerToHeaderInfo(hdr)
+	hInfo, err := headerToHeaderInfo(hdr)
+	if err != nil {
+		return err
+	}
 
 	if err := b.hashCache.AddIfNotPresent(hInfo); err != nil {
 		return err
```

### beacon-chain/powchain/block_cache_test.go
```diff
@@ -2,6 +2,7 @@ package powchain
 
 import (
 	"math/big"
+	"reflect"
 	"testing"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -102,3 +103,47 @@ func TestBlockCache_maxSize(t *testing.T) {
 	assert.Equal(t, int(maxCacheSize), len(cache.hashCache.ListKeys()))
 	assert.Equal(t, int(maxCacheSize), len(cache.heightCache.ListKeys()))
 }
+
+func Test_headerToHeaderInfo(t *testing.T) {
+	type args struct {
+		hdr *gethTypes.Header
+	}
+	tests := []struct {
+		name    string
+		args    args
+		want    *headerInfo
+		wantErr bool
+	}{
+		{
+			name: "OK",
+			args: args{hdr: &gethTypes.Header{
+				Number: big.NewInt(500),
+				Time:   2345,
+			}},
+			want: &headerInfo{
+				Number: big.NewInt(500),
+				Hash:   common.Hash{239, 10, 13, 71, 156, 192, 23, 93, 73, 154, 255, 209, 163, 204, 129, 12, 179, 183, 65, 70, 205, 200, 57, 12, 17, 211, 209, 4, 104, 133, 73, 86},
+				Time:   2345,
+			},
+		},
+		{
+			name: "nil number",
+			args: args{hdr: &gethTypes.Header{
+				Time: 2345,
+			}},
+			wantErr: true,
+		},
+	}
+	for _, tt := range tests {
+		t.Run(tt.name, func(t *testing.T) {
+			got, err := headerToHeaderInfo(tt.args.hdr)
+			if (err != nil) != tt.wantErr {
+				t.Errorf("headerToHeaderInfo() error = %v, wantErr %v", err, tt.wantErr)
+				return
+			}
+			if !reflect.DeepEqual(got, tt.want) {
+				t.Errorf("headerToHeaderInfo() got = %v, want %v", got, tt.want)
+			}
+		})
+	}
+}
```

### beacon-chain/powchain/block_reader.go
```diff
@@ -229,7 +229,10 @@ func (s *Service) retrieveHeaderInfo(ctx context.Context, bNum uint64) (*headerI
 		if err := s.headerCache.AddHeader(blk); err != nil {
 			return nil, err
 		}
-		info = headerToHeaderInfo(blk)
+		info, err = headerToHeaderInfo(blk)
+		if err != nil {
+			return nil, err
+		}
 	}
 	return info, nil
 }
```
