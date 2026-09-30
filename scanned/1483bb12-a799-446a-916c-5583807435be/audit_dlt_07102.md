# [?] Resolve panic on shutdown with offline eth1 node (#8033)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2020-12-07
Source: https://github.com/OffchainLabs/prysm/commit/fbbdd94fea18a913a6e7a397c68e61b1c4b02bed
Type: security-commit

## Details
Resolve panic on shutdown with offline eth1 node (#8033)

* Resolve panic on shutdown with offline eth1 node

* Move fix tne right place nishant feedback

* fix log message

Co-authored-by: Nishant Das <nishdas93@gmail.com>

## Patch
### beacon-chain/powchain/service.go
```diff
@@ -255,6 +255,10 @@ func (s *Service) Start() {
 	}
 	go func() {
 		s.waitForConnection()
+		if s.ctx.Err() != nil {
+			log.Info("Context closed, exiting pow goroutine")
+			return
+		}
 		s.run(s.ctx.Done())
 	}()
 }
@@ -674,7 +678,6 @@ func (s *Service) initPOWService() {
 			return
 		default:
 			ctx := s.ctx
-
 			header, err := s.eth1DataFetcher.HeaderByNumber(ctx, nil)
 			if err != nil {
 				log.Errorf("Unable to retrieve latest ETH1.0 chain header: %v", err)
```
