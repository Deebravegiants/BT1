### Title
Database credentials (including password) exposed via `pg_dump` process command-line arguments during periodic backup - (File: core/services/periodicbackup/backup.go)

### Summary
The Chainlink node's periodic database backup feature passes the full, unredacted PostgreSQL connection string — including the plaintext password — as a command-line argument to the `pg_dump` subprocess. Any local unprivileged user with process-listing access on the host (e.g., via `ps aux` or reading `/proc/<pid>/cmdline`) can capture the database credentials while a backup is running, exactly mirroring the root cause of CVE-2018-17957 (SUSE RMT exposing MySQL passwords via process commandline).

### Finding Description
In `runBackup`, the raw database URL is built into the `pg_dump` argument list and executed directly: [1](#0-0) 

The code does construct a masking helper (`maskArgs`) that redacts the URL via `backup.databaseURL.Redacted()`, but this masked copy is used **only for the debug log line** (`backup.logger.Debugf("Running pg_dump with: %v", maskedArgs)`). The actual subprocess invocation, `exec.Command("pg_dump", args...)`, still receives the unmasked `args` slice whose first element is `backup.databaseURL.String()` — the full connection string with credentials in the clear: [2](#0-1) 

On Linux, process arguments passed via `exec` are visible to any local user via `/proc/<pid>/cmdline` or standard process-listing tools (`ps`, `top`) unless the kernel/OS specifically restricts this (not the default on most distros/containers). This is the same vulnerability class as CVE-2018-17957: a database password is placed on a subprocess's command line instead of being passed through a safer channel (env var, PGPASSFILE, stdin, or a temporary `.pgpass`/service file), allowing any co-located unprivileged local process/user to harvest the credential.

Notably, elsewhere in the same codebase the project treats database URLs as sensitive by default — the `SecretURL`/`SecretString` types redact when formatted (`core/store/models/secrets.go`) and config validation/logging paths (e.g., `core/config/toml/types.go`, `core/web/router.go`'s `readSanitizedJSON`/`redact`) go out of their way to avoid leaking secrets — showing that the intended security posture requires suppressing DB credentials from any observable surface. The `runBackup` function violates that same policy at the OS process boundary.

### Impact Explanation
If the periodic backup feature (`Database.Backup.Mode` != `none`) is enabled — which is common in production Chainlink node deployments — the live Postgres password is exposed to any other unprivileged local process/user on the host for the duration of each backup run (which can be long for large databases). An attacker with local access (e.g., a compromised sidecar container sharing the process namespace, another unprivileged account, or an attacker who achieved limited code execution elsewhere on the host) can read this password and directly authenticate to the Chainlink database, potentially reading/corrupting job specs, keys, and other sensitive on-chain-related state — consistent with the "C:H/I:H/A:H" impact rated for the original CVE.

### Likelihood Explanation
Any node with `Database.Backup.Frequency` > 0 runs this code path automatically and periodically (`Start` sets up a ticker calling `RunBackup`) with no user interaction required, so the exposure window recurs on every backup cycle for as long as `pg_dump` executes: [3](#0-2) 

The only precondition is local access to the host/container running the node (e.g., shared PID namespace, container escape, or another local account) — no privileged/administrative Chainlink access is required to observe already-running process arguments.

### Recommendation
Do not pass the database URL (or any secret) as a `pg_dump` command-line argument. Use one of:
- Set `PGPASSWORD` (or better, a `PGPASSFILE`/`.pgpass` entry, or the `service=` connection method) as an environment variable / file readable only by the node process, and pass only host/port/user/dbname as non-secret CLI args.
- Alternatively, pipe connection parameters via `PGSERVICE` or `libpq` connection URI passed through an environment variable rather than argv, since env vars set via `cmd.Env` are not visible via `ps`/`/proc/<pid>/cmdline` (though still visible via `/proc/<pid>/environ` to same-UID processes, which is a materially smaller exposure surface).
- Ensure the already-existing `maskArgs`/`Redacted()` masking is used consistently — currently it only protects the log line, not the actual subprocess invocation, giving a false sense of security.

### Proof of Concept
1. Configure a node with `[Database.Backup] Mode = "full"` (or `"lite"`) and `Frequency = "1m"`.
2. While a backup is running, on the same host run `ps aux | grep pg_dump` or `cat /proc/$(pgrep pg_dump)/cmdline | tr '\0' ' '`.
3. Observe the full `postgresql://user:password@host:port/dbname?...` string, including the plaintext password, in the process argument list — confirmed by the code path at [1](#0-0)  where `args[0]` (unredacted) is passed directly to `exec.Command`.

### Citations

**File:** core/services/periodicbackup/backup.go (L101-113)
```go
		go func() {
			for {
				select {
				case <-backup.done:
					ticker.Stop()
					return
				case <-ticker.C:
					backup.logger.Infow("Starting automatic database backup, this can take a while. To disable periodic backups, set Database.Backup.Frequency=0. To disable database backups entirely, set Database.Backup.Mode=none.")
					//nolint:errcheck
					backup.RunBackup(static.Version)
				}
			}
		}()
```

**File:** core/services/periodicbackup/backup.go (L166-190)
```go
	args := []string{
		backup.databaseURL.String(),
		"-f", tmpFile.Name(),
		"-F", "c", // format: custom (zipped)
	}

	if backup.mode == config.DatabaseBackupModeLite {
		for _, table := range excludedDataFromTables {
			args = append(args, "--exclude-table-data="+table)
		}
	}

	maskArgs := func(args []string) []string {
		masked := make([]string, len(args))
		copy(masked, args)
		masked[0] = backup.databaseURL.Redacted()
		return masked
	}

	maskedArgs := maskArgs(args)
	backup.logger.Debugf("Running pg_dump with: %v", maskedArgs)

	cmd := exec.Command(
		"pg_dump", args...,
	)
```
