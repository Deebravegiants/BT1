# [H] Capgo CLI: symlink-following local secret writes enable arbitrary file overwrite + world-readable credentials (0600 missing)

## Summary
Severity: High
Advisory: GHSA-8mpm-q7mh-8fvh
CWE: CWE-276, CWE-377, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-8mpm-q7mh-8fvh
Type: github-advisory

## Affected
- npm: `@capgo/cli` — affected >=0 <7.84.6

## Details
### Summary
The Capgo CLI writes sensitive local files (.capgo API key file and build credentials JSON) using unsafe file operations that follow symlinks and do not enforce safe permissions. This allows an attacker-controlled repository to cause arbitrary file overwrite on the developer’s machine when the developer runs the CLI inside that repo. Additionally, global build credentials are written with world-readable permissions (664), exposing signing materials on shared systems.

### Details
Issue 1 - Arbitrary file overwrite via .capgo symlink (login --local)

- Location: src/login.ts
- Behavior: loginInternal(..., { local: true }) performs writeFileSync('.capgo', ...) before validating the API key with verifyUser().
- No checks are performed to prevent writing through a symlink.
- Result: if .capgo is a symlink to an arbitrary path, the CLI overwrites the symlink target with attacker-controlled content (the provided API key string), even when login fails.

Issue 2 - Arbitrary file overwrite via .capgo-credentials.json symlink (build credentials save --local)

- Location: src/build/credentials.ts (local path is join(cwd(), '.capgo-credentials.json'))
- Behavior: credentials are written using writeFile() without checking whether the destination is a symlink.
- Result: if .capgo-credentials.json is a symlink to an arbitrary path, the CLI overwrites the symlink target with attacker-controlled JSON (including base64-encoded credential material). This occurs even if the user is not logged in / no API key exists.

Issue 3 - Insecure default permissions for global credentials

- Location: src/build/credentials.ts (global path $HOME/.capgo-credentials/credentials.json)
- Observed permissions after save: -rw-rw-r-- (664)
- Impact: credentials file contains sensitive signing material (e.g., Android keystore + Play config; iOS cert/profile/API key in other flows). World/group readability is unsafe on shared hosts and CI runners. Expected minimum: file 0600, directory 0700.

### PoC
PoC A: .capgo symlink clobber (writes even when API key invalid)
```
set -euo pipefail
BASE="/tmp/capgo_cli_poc_$(date +%s)"
HOME_SANDBOX="$BASE/home"
REPO="$BASE/repo"
TARGET="$BASE/clobbered.txt"

mkdir -p "$HOME_SANDBOX" "$REPO"
cd "$REPO"
git init -q

ln -s "$TARGET" .capgo

# This should fail auth, but still overwrites TARGET
HOME="$HOME_SANDBOX" npx --yes @capgo/cli@7.82.0 login "INVALID_KEY_SHOULD_FAIL" --local || true

echo "== TARGET content =="
cat "$TARGET"
```
_Expected: On invalid key, nothing is written; .capgo should never follow symlinks.
Observed: TARGET contains INVALID_KEY_SHOULD_FAIL._

PoC B: .capgo-credentials.json symlink clobber (no login required)
```
set -euo pipefail
BASE="/tmp/capgo_creds_symlink_$(date +%s)"
HOME_SANDBOX="$BASE/home"
REPO="$BASE/repo"
TARGET="$BASE/clobbered_creds.txt"

mkdir -p "$HOME_SANDBOX" "$REPO"
cd "$REPO"
git init -q

ln -s "$TARGET" .capgo-credentials.json

HOME="$HOME_SANDBOX" npx --yes @capgo/cli@7.82.0 build credentials save \
  --local --platform android --appId com.example.app \
  --keystore /etc/hosts --keystore-alias x --keystore-key-password x --play-config /etc/hosts || true

echo "== TARGET exists and contains JSON written via symlink =="
ls -la "$TARGET" || true
cat "$TARGET" || true
```
_Expected: Refuse to write if destination is symlink; ideally require safe location and permissions.
Observed: TARGET is created/overwritten with credentials JSON._

PoC C: global credentials permissions are world-readable
```
set -euo pipefail
BASE="/tmp/capgo_creds_perm_$(date +%s)"
HOME_SANDBOX="$BASE/home"
mkdir -p "$HOME_SANDBOX"

HOME="$HOME_SANDBOX" npx --yes @capgo/cli@7.82.0 build credentials save \
  --platform android --appId com.example.app \
  --keystore /etc/hosts --keystore-alias x --keystore-key-password x --play-config /etc/hosts || true

CREDS="$HOME_SANDBOX/.capgo-credentials/credentials.json"
ls -la "$CREDS" || true
stat -c '%a %U:%G %n' "$CREDS" || true
```
_Observed: credentials.json created with mode 664 (-rw-rw-r--)._

### Impact

- Arbitrary file overwrite (clobber) as the user running the CLI (developer workstation / CI runner).
- This can cause:

>developer environment compromise or sabotage (overwriting config files, scripts, env files)
>accidental or malicious leakage/destruction of secrets

- Local secret exposure: global credentials written as 664 allows other local users to read signing material on shared machines.
- A realistic scenario: a developer runs npx @capgo/cli ... --local inside an untrusted repo/template; the repo contains malicious symlinks.

### Suggested remediation

- Do not write .capgo until after API key validation succeeds.
- For all secret/config writes:

>refuse symlink destinations (lstat + isSymbolicLink)
>use safe file creation and enforce permissions (0600 for files; 0700 for directories)
>write atomically (temp file + rename) after safety checks

- Avoid blindly appending to .gitignore unless it is a regular file (also check for symlink).

## References
- https://github.com/Cap-go/capgo/security/advisories/GHSA-8mpm-q7mh-8fvh
- https://github.com/Cap-go/CLI/commit/b8aa5ccbfad2d7f10f3cdbc00910d4a6aab026b2
- https://github.com/Cap-go/capgo
