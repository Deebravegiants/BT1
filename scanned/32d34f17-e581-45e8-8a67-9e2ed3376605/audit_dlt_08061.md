# [?] cmd/puppeth: fix nil panic on disconnected stats gathering

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-08-16
Source: https://github.com/celo-org/celo-blockchain/commit/b24fb76a3ae8b2a41bde9ed0744b4284e385e011
Type: security-commit

## Details
cmd/puppeth: fix nil panic on disconnected stats gathering

## Patch
### cmd/puppeth/wizard_netstats.go
```diff
@@ -82,7 +82,6 @@ func (w *wizard) gatherStats(server string, pubkey []byte, client *sshClient) *s
 	logger.Info("Starting remote server health-check")
 
 	stat := &serverStat{
-		address:  client.address,
 		services: make(map[string]map[string]string),
 	}
 	if client == nil {
@@ -94,6 +93,8 @@ func (w *wizard) gatherStats(server string, pubkey []byte, client *sshClient) *s
 		}
 		client = conn
 	}
+	stat.address = client.address
+
 	// Client connected one way or another, run health-checks
 	logger.Debug("Checking for nginx availability")
 	if infos, err := checkNginx(client, w.network); err != nil {
@@ -214,6 +215,9 @@ func (stats serverStats) render() {
 		if len(stat.address) > len(separator[1]) {
 			separator[1] = strings.Repeat("-", len(stat.address))
 		}
+		if len(stat.failure) > len(separator[1]) {
+			separator[1] = strings.Repeat("-", len(stat.failure))
+		}
 		for service, configs := range stat.services {
 			if len(service) > len(separator[2]) {
 				separator[2] = strings.Repeat("-", len(service))
@@ -250,7 +254,11 @@ func (stats serverStats) render() {
 		sort.Strings(services)
 
 		if len(services) == 0 {
-			table.Append([]string{server, stats[server].address, "", "", ""})
+			if stats[server].failure != "" {
+				table.Append([]string{server, stats[server].failure, "", "", ""})
+			} else {
+				table.Append([]string{server, stats[server].address, "", "", ""})
+			}
 		}
 		for j, service := range services {
 			// Add an empty line between all services
```
