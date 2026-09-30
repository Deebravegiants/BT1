# [?] beacon-chain/execution: fix a data race in testcase (#13016)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2023-10-11
Source: https://github.com/OffchainLabs/prysm/commit/d7318ea485adad0ad7e82ff526933a1f450aff14
Type: security-commit

## Details
beacon-chain/execution: fix a data race in testcase (#13016)

Signed-off-by: jsvisa <delweng@gmail.com>
Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>
Co-authored-by: Nishant Das <nishdas93@gmail.com>

## Patch
### beacon-chain/execution/block_reader_test.go
```diff
@@ -48,6 +48,8 @@ func TestLatestMainchainInfo_OK(t *testing.T) {
 	require.NoError(t, err)
 	testAcc.Backend.Commit()
 
+	tickerChan := make(chan time.Time)
+	web3Service.eth1HeadTicker = &time.Ticker{C: tickerChan}
 	exitRoutine := make(chan bool)
 
 	go func() {
@@ -58,8 +60,6 @@ func TestLatestMainchainInfo_OK(t *testing.T) {
 	header, err := web3Service.HeaderByNumber(web3Service.ctx, nil)
 	require.NoError(t, err)
 
-	tickerChan := make(chan time.Time)
-	web3Service.eth1HeadTicker = &time.Ticker{C: tickerChan}
 	tickerChan <- time.Now()
 	web3Service.cancel()
 	exitRoutine <- true
```
