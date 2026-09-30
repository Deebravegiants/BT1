# [?] Fix KafkaSuite.TearDownTest to not crash

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-06-07
Source: https://github.com/kaiachain/kaia/commit/993bd982bd3c5d11877bc25df201304f573a0d59
Type: security-commit

## Details
Fix KafkaSuite.TearDownTest to not crash

s.kfk can be nil when there is no kafka instance

## Patch
### datasync/chaindatafetcher/kafka/kafka_test.go
```diff
@@ -65,7 +65,9 @@ func (s *KafkaSuite) SetupTest() {
 }
 
 func (s *KafkaSuite) TearDownTest() {
-	s.kfk.Close()
+	if s.kfk != nil {
+		s.kfk.Close()
+	}
 }
 
 func (s *KafkaSuite) TestKafka_split() {
```
