# [?] fix(das): avoid possible nil deref case

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2021-11-23
Source: https://github.com/celestiaorg/celestia-node/commit/092125200ca9e5d8e984aa2d08b3420b97499c87
Type: security-commit

## Details
fix(das): avoid possible nil deref case

## Patch
### das/daser.go
```diff
@@ -75,7 +75,9 @@ func (d *DASer) sampling(ctx context.Context, sub header.Subscription) {
 			if err == context.Canceled {
 				return
 			}
+
 			log.Errorw("DASer failed to get next header", "err", err)
+			continue
 		}
 
 		startTime := time.Now()
```

### service/header/subscription.go
```diff
@@ -37,7 +37,7 @@ func (s *subscription) NextHeader(ctx context.Context) (*ExtendedHeader, error)
 	var header ExtendedHeader
 	err = header.UnmarshalBinary(msg.Data)
 	if err != nil {
-		log.Errorw("unmarshalling data from message", "err")
+		log.Errorw("unmarshalling data from message", "err", err)
 		return nil, err
 	}
 
```
