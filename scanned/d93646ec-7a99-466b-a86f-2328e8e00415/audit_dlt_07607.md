# [?] cm/puppeth: fix crash when of ethstats specifier doesn't contain `:` (#25405)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2022-07-29
Source: https://github.com/ethereum/go-ethereum/commit/1af9e4f34caccc6bdc30c151b74f9689f5627c6d
Type: security-commit

## Details
cm/puppeth: fix crash when of ethstats specifier doesn't contain `:` (#25405)


Signed-off-by: Delweng <delweng@gmail.com>

## Patch
### cmd/puppeth/module.go
```diff
@@ -150,3 +150,12 @@ func checkPort(host string, port int) error {
 	conn.Close()
 	return nil
 }
+
+// getEthName gets the Ethereum Name from ethstats
+func getEthName(s string) string {
+	n := strings.Index(s, ":")
+	if n >= 0 {
+		return s[:n]
+	}
+	return s
+}
```

### cmd/puppeth/module_explorer.go
```diff
@@ -104,7 +104,7 @@ func deployExplorer(client *sshClient, network string, bootnodes []string, confi
 		"Datadir":     config.node.datadir,
 		"DBDir":       config.dbdir,
 		"EthPort":     config.node.port,
-		"EthName":     config.node.ethstats[:strings.Index(config.node.ethstats, ":")],
+		"EthName":     getEthName(config.node.ethstats),
 		"WebPort":     config.port,
 		"Transformer": transformer,
 	})
```

### cmd/puppeth/module_faucet.go
```diff
@@ -116,7 +116,7 @@ func deployFaucet(client *sshClient, network string, bootnodes []string, config
 		"VHost":         config.host,
 		"ApiPort":       config.port,
 		"EthPort":       config.node.port,
-		"EthName":       config.node.ethstats[:strings.Index(config.node.ethstats, ":")],
+		"EthName":       getEthName(config.node.ethstats),
 		"CaptchaToken":  config.captchaToken,
 		"CaptchaSecret": config.captchaSecret,
 		"FaucetAmount":  config.amount,
```

### cmd/puppeth/module_node.go
```diff
@@ -123,7 +123,7 @@ func deployNode(client *sshClient, network string, bootnodes []string, config *n
 		"TotalPeers": config.peersTotal,
 		"Light":      config.peersLight > 0,
 		"LightPeers": config.peersLight,
-		"Ethstats":   config.ethstats[:strings.Index(config.ethstats, ":")],
+		"Ethstats":   getEthName(config.ethstats),
 		"Etherbase":  config.etherbase,
 		"GasTarget":  config.gasTarget,
 		"GasLimit":   config.gasLimit,
```
