# [M] linuxfabrik-lib: Arbitrary root file read via live --test argument (lib.lftest) across sudoers-whitelisted plugins (LPE)

## Summary
Severity: Medium
Advisory: GHSA-rh9c-rqvg-f7pr
CVE: CVE-2026-73974
CWE: CWE-22, CWE-269
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-rh9c-rqvg-f7pr
Type: github-advisory

## Affected
- PyPI: `linuxfabrik-lib` — affected >=0 <6.1.0

## Details
## Summary
Every Linuxfabrik check plugin that supports the shared `--test` argument (routed through `lib.lftest.test()`) will, when `--test` is supplied, treat the first CSV element as a filesystem path and read its full contents as the plugin's simulated STDOUT — running as root when the plugin is invoked through the shipped `nagios`/`icinga` sudoers allowlist. `--test` is a **live production argument** (centrally mapped to `argparse.SUPPRESS`, so it is hidden from `--help` but still accepted on the command line), not a build-time-only gate. This yields an arbitrary root file-read primitive (full disclosure on `deb-updates`; filtered disclosure / existence-and-readability oracle on ~22 other whitelisted plugins), i.e. local privilege escalation from the `nagios` account to root.

## Root Cause
- `lib.lftest.test(args)` (`lftest.py` lines 659-664): `stdout = args[0]`; `if stdout and os.path.isfile(stdout): _, stdout = disk.read_file(stdout)`. Element[1] (stderr channel) is read the same way. There is **no path confinement** on the supplied path.
- `check-plugins/deb-updates/deb-updates`: `--test` is registered with `type=lib.args.csv` (lines 78-82). When supplied, control flows to `stdout, _, retc = lib.lftest.test(args.TEST)` (line 143), bypassing the apt path (`if args.TEST is None:` at 121). Each returned line is stored as a `package` row and, under the default `--query='1'` (`WHERE 1`, matches all rows), every row is printed via `'\n* '.join([row['package'] ...])` → `lib.base.oao(...)`.
- The same `--test`/`lib.lftest.test()` mechanism exists identically on ~22 whitelisted plugins (e.g. `docker-info`), each performing a root `open()`/read of the attacker-named path. Disclosure degree varies by each plugin's downstream parser: full (`deb-updates`), filtered (`docker-info` echoes lines containing `warning:`/`error:`; `openvpn-client-list` echoes `CLIENT_LIST` lines), or existence/readability oracle (JSON parsers).

## Impact
An attacker controlling the low-privilege `nagios`/`icinga` account (the documented threat model for the shipped sudoers file — same precondition as CVE-2026-52817) obtains the full contents of any root-readable file via `deb-updates` (e.g. `/etc/shadow`, `/root/.ssh/id_*`, TLS keys, cloud credentials), plus a fleet-wide root file existence/readability oracle and filtered content leak via the other plugins → local privilege escalation to root.

## Proof of Concept
Full disclosure (deb-updates):
```
sudo /usr/lib64/nagios/plugins/deb-updates --test=/etc/shadow,,0
```
Filtered disclosure / oracle (docker-info, target routed to the stderr channel that gets echoed):
```
sudo /usr/lib64/nagios/plugins/docker-info --test="dummy,/etc/shadow,0"
```

## Attack Chain
1. **Entry:** `sudo /usr/lib64/nagios/plugins/deb-updates --test=/etc/shadow,,0`
   - **Action:** the nagios user invokes the whitelisted plugin as root with a `--test` CSV whose element[0] is the target path and retc=0.
   - **Guard:** sudoers (Debian.sudoers:3) lists the binary only; `--test` is not gated to test builds.
   - **Bypass proof:** CONTRIBUTING.md documents `--test` as centrally mapped to `argparse.SUPPRESS` — hidden from `--help` but still accepted on the command line; `lib.args.csv` splits `/etc/shadow,,0` into `['/etc/shadow','','0']`.
2. **Sink:** `lib.lftest.test(args.TEST)` (deb-updates:143) reads element[0] as a file, as root.
   - **Guard:** none — no path confinement on element[0].
   - **Bypass proof (from lib source):** `lftest.py:661-664`: `stdout = args[0]; if stdout and os.path.isfile(stdout): _, stdout = disk.read_file(stdout)` — element[0], if it exists on disk, is opened and its contents returned as stdout. `retc=0` (element[2]) so there is no early `cu()` abort.
3. **Store + query:** each line → `lib.db_sqlite.insert(conn, {'package': item}, ...)`; default `QUERY='1'` → `SELECT * FROM deb_updates WHERE 1`.
   - **Guard:** `--only-critical` or a restrictive `--query` would filter, but both default to permissive (`ONLY_CRITICAL=False`, `QUERY='1'`).
   - **Bypass proof:** attacker passes neither → all rows selected.
4. **Disclosure:** `msg += '\n* '.join([row['package'] for row in result])` → `lib.base.oao(...)` → stdout.
   - **Guard:** none.
   - **Bypass proof:** with `len(result) > 0` the branch prints every row (every file line).
5. **Impact:** full contents of any root-readable file disclosed to the nagios user → root. On the ~22 other `--test` plugins the same primitive yields a filtered leak / universal root file existence-and-readability oracle.

## Bypass Evidence
- `lib.lftest.test()` file-read behavior verified directly from linuxfabrik-lib source (`lftest.py:659-664`, `disk.read_file(stdout)` when `os.path.isfile(stdout)`).
- `--test` registration (`type=lib.args.csv`) and the `stdout, _, retc = lib.lftest.test(args.TEST)` call verified on the latest release tag **v6.0.0** at `check-plugins/deb-updates/deb-updates:143` (GitHub contents API); default `QUERY='1'` confirmed.
- No path-confinement guard exists on the `--test` path element in either the plugin or `lib.lftest`.

## Affected Versions
`<= 6.0.0` (latest release; `--test`/`lib.lftest.test()` flow present on tag v6.0.0). Not covered by any existing advisory (none reference `--test` or arbitrary file read).

## Suggested Fix
Compile `--test` out of production builds (or gate it behind an explicit build/dev flag so it is not accepted at runtime), OR confine the `--test` path element(s) to a dedicated fixtures directory via `realpath()` + containment check before `disk.read_file()`. As defense-in-depth, constrain the sudoers entries to specific argument values so `--test` cannot be supplied to a root-run plugin.

---
Reported by **zx (Jace)**

## References
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-rh9c-rqvg-f7pr
- https://github.com/Linuxfabrik/lib/commit/d665042c55fae83a295ebc0023e8b77f6c473a28
- https://github.com/Linuxfabrik/lib/releases/tag/v6.1.0
- https://github.com/Linuxfabrik/monitoring-plugins
