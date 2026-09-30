# [?] tests: fix network metrics race condition in tests (#4529)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-09-12
Source: https://github.com/algorand/go-algorand/commit/794a63ddc42df5b348e0c2f5f86b7178def457d8
Type: security-commit

## Details
tests: fix network metrics race condition in tests (#4529)

## Patch
### network/wsPeer_test.go
```diff
@@ -18,7 +18,6 @@ package network
 
 import (
 	"encoding/binary"
-	"fmt"
 	"strings"
 	"testing"
 	"time"
@@ -115,7 +114,7 @@ func TestTagCounterFiltering(t *testing.T) {
 		"networkMessageSentByTag":     networkMessageSentByTag,
 	}
 	for name, tag := range tagCounterTags {
-		t.Run(fmt.Sprintf("%s", name), func(t *testing.T) {
+		t.Run(name, func(t *testing.T) {
 			require.NotZero(t, len(tag.AllowedTags))
 			tag.Add("TEST_TAG", 1)
 			b := strings.Builder{}
```

### util/metrics/tagcounter.go
```diff
@@ -104,16 +104,13 @@ func (tc *TagCounter) Add(tag string, val uint64) {
 			var st []uint64
 			if len(tc.storage) > 0 {
 				st = tc.storage[len(tc.storage)-1]
-				//fmt.Printf("new tag %v, old block\n", tag)
 			}
 			if tc.storagePos > (len(st) - 1) {
-				//fmt.Printf("new tag %v, new block\n", tag)
 				st = make([]uint64, 16)
 				tc.storagePos = 0
 				tc.storage = append(tc.storage, st)
 			}
 			newtags[tag] = &(st[tc.storagePos])
-			//fmt.Printf("tag %v = %p\n", tag, newtags[tag])
 			tc.storagePos++
 			tc.tags = newtags
 			tc.tagptr.Store(newtags)
@@ -155,7 +152,8 @@ func (tc *TagCounter) WriteMetric(buf *strings.Builder, parentLabels string) {
 			buf.WriteRune('}')
 		}
 		buf.WriteRune(' ')
-		buf.WriteString(strconv.FormatUint(*tagcount, 10))
+		count := atomic.LoadUint64(tagcount)
+		buf.WriteString(strconv.FormatUint(count, 10))
 		buf.WriteRune('\n')
 	}
 }
@@ -179,6 +177,7 @@ func (tc *TagCounter) AddMetric(values map[string]float64) {
 		} else {
 			name = tc.Name + "_" + tag
 		}
-		values[sanitizeTelemetryName(name)] = float64(*tagcount)
+		count := atomic.LoadUint64(tagcount)
+		values[sanitizeTelemetryName(name)] = float64(count)
 	}
 }
```
