# [?] docs: add security vulnerability disclosure policy (#8978)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-05
Source: https://github.com/fedimint/fedimint/commit/fbc127fe1f4b94da9d670c1f2706ef9dcdddaafc
Type: security-commit

## Details
docs: add security vulnerability disclosure policy (#8978)

### Summary

Adds a root `SECURITY.md` establishing a private vulnerability
disclosure channel. Until now the repo had no security policy anywhere,
so anyone finding a vulnerability had no sanctioned option besides a
public issue.

### Details

Reports go to **security@fedimint.org** (forwards to dpc and elsirion)
or to `@elsirion.21` on Signal. For sensitive reports the policy lists
both maintainers' PGP key fingerprints and how to fetch the keys from
the Proton key server. It also states supported versions (latest stable
release line only) and scopes out threshold-guardian collusion and bugs
in third-party dependencies. It deliberately makes no process or SLA
commitments.

### Reviewing

- @dpc please confirm your listed key fingerprint (`23B8 147B 42EB 74CB
801F F76F 930E AF17 AB8F F29C`) and that security@fedimint.org
forwarding reaches you.
- GitHub private vulnerability reporting is currently disabled on this
repo; we could enable it and list it as an additional channel, but the
policy works without it.

### Testing

Docs-only change; `just final-lint` passes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01BLtSHuk4w9fecCsn5CP7c1

## Patch
### SECURITY.md
```diff
@@ -0,0 +1,60 @@
+# Security Policy
+
+## Reporting a Vulnerability
+
+Do **not** open a public GitHub issue for security bugs.
+
+Send a report to **security@fedimint.org** (this address forwards to the
+maintainers listed below) or message **`@elsirion.21`** on Signal.
+
+Please include:
+
+- What the bug is and where it is in the code.
+- How to reproduce it, if possible.
+- What an attacker can do with it (steal funds, break consensus, leak user
+  data, stop the federation, etc.).
+- Your name or handle, if you want credit in the fix announcement.
+
+## Encrypted Reports
+
+If the report is sensitive, encrypt it with PGP. Mail sent to
+security@fedimint.org goes to both maintainers, so encrypt to **both keys**.
+
+| Maintainer | Email | Key fingerprint |
+| --- | --- | --- |
+| dpc | `dpc@dpc.pw` | `23B8 147B 42EB 74CB 801F F76F 930E AF17 AB8F F29C` |
+| elsirion | `elsirion@protonmail.com` | `B3CD FF6F 6D4B 2BE9 EA8B 0020 B300 5E57 1AA3 14DA` |
+
+Both keys are hosted on the Proton Mail key server. To fetch them:
+
+```sh
+gpg --fetch-keys 'https://api.protonmail.ch/pks/lookup?op=get&search=dpc@dpc.pw'
+gpg --fetch-keys 'https://api.protonmail.ch/pks/lookup?op=get&search=elsirion@protonmail.com'
+```
+
+Check the fingerprints against the table above before you use the keys.
+
+Please keep the bug private until a fix is released and federation operators
+had time to upgrade.
+
+## Supported Versions
+
+We only fix security bugs in the latest stable release line. Older releases do
+not get patches. Run a current release if you run a federation in production.
+
+## Scope
+
+In scope:
+
+- All code in this repository: `fedimintd`, `fedimint-cli`, the client
+  libraries, the modules (mint, wallet, lightning, meta) and the gateway.
+- Consensus safety, fund safety, user privacy, and denial of service against a
+  federation.
+
+Out of scope:
+
+- Bugs in third-party software we depend on (report them upstream, but tell us
+  too if Fedimint is affected).
+- Attacks that need a majority of guardians to be malicious. The threat model
+  assumes fewer than one third of guardians are faulty.
+- Test and development setups, such as `devimint`.
```
