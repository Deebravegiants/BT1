# [?] whisper: serious security issue fixed (#16219)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-03-01
Source: https://github.com/celo-org/celo-blockchain/commit/5a150e1b7724c91009a237ab0879cd64844b390d
Type: security-commit

## Details
whisper: serious security issue fixed (#16219)

The diagnostic tool was saving the unencrypted version of the messages, which is an obvious
security flaw. As of this commit:
  * encrypted messages saved instead of plain text.
  * all messages are stored, even that created by the user of wnode.

## Patch
### cmd/wnode/main.go
```diff
@@ -594,19 +594,22 @@ func writeMessageToFile(dir string, msg *whisper.ReceivedMessage) {
 		address = crypto.PubkeyToAddress(*msg.Src)
 	}
 
-	if whisper.IsPubKeyEqual(msg.Src, &asymKey.PublicKey) {
-		// message from myself: don't save, only report
-		fmt.Printf("\n%s <%x>: message received: '%s'\n", timestamp, address, name)
-	} else if len(dir) > 0 {
+	// this is a sample code; uncomment if you don't want to save your own messages.
+	//if whisper.IsPubKeyEqual(msg.Src, &asymKey.PublicKey) {
+	//	fmt.Printf("\n%s <%x>: message from myself received, not saved: '%s'\n", timestamp, address, name)
+	//	return
+	//}
+
+	if len(dir) > 0 {
 		fullpath := filepath.Join(dir, name)
-		err := ioutil.WriteFile(fullpath, msg.Payload, 0644)
+		err := ioutil.WriteFile(fullpath, msg.Raw, 0644)
 		if err != nil {
 			fmt.Printf("\n%s {%x}: message received but not saved: %s\n", timestamp, address, err)
 		} else {
-			fmt.Printf("\n%s {%x}: message received and saved as '%s' (%d bytes)\n", timestamp, address, name, len(msg.Payload))
+			fmt.Printf("\n%s {%x}: message received and saved as '%s' (%d bytes)\n", timestamp, address, name, len(msg.Raw))
 		}
 	} else {
-		fmt.Printf("\n%s {%x}: big message received (%d bytes), but not saved: %s\n", timestamp, address, len(msg.Payload), name)
+		fmt.Printf("\n%s {%x}: message received (%d bytes), but not saved: %s\n", timestamp, address, len(msg.Raw), name)
 	}
 }
 
```
