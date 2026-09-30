# [?] Fix for panic in signature verification if a peer sends a nil public key.

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-09-20
Source: https://github.com/cometbft/cometbft/commit/ebfaf30705c38746ff05377eaf3199ebf497ffdd
Type: security-commit

## Details
Fix for panic in signature verification if a peer sends a nil public key.

## Patch
### p2p/conn/secret_connection.go
```diff
@@ -133,6 +133,11 @@ func MakeSecretConnection(conn io.ReadWriteCloser, locPrivKey crypto.PrivKey) (*
 	}
 
 	remPubKey, remSignature := authSigMsg.Key, authSigMsg.Sig
+
+	if remPubKey == nil {
+		return nil, errors.New("Peer sent a nil public key")
+	}
+
 	if !remPubKey.VerifyBytes(challenge[:], remSignature) {
 		return nil, errors.New("Challenge verification failed")
 	}
```
