# [?] [FAB-14816] Fix data race in comm test

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-03-26
Source: https://github.com/hyperledger/fabric/commit/454e6327f9a0f781e066b42b5a7e5b75d1172546
Type: security-commit

## Details
[FAB-14816] Fix data race in comm test

Change-Id: If53a60876a6858c187899f5899ba5872139c3777
Signed-off-by: Gari Singh <gari.r.singh@gmail.com>

## Patch
### core/comm/server_test.go
```diff
@@ -1668,7 +1668,7 @@ func TestCipherSuites(t *testing.T) {
 				RootCAs:      certPool,
 				CipherSuites: test.clientCiphers,
 			}
-			_, err = tls.Dial("tcp", testAddress, tlsConfig)
+			_, err := tls.Dial("tcp", testAddress, tlsConfig)
 			if test.success {
 				assert.NoError(t, err)
 			} else {
```
