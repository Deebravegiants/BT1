# [M] Traefik: A timing side-channel vulnerability allows for valid username enumeration via BasicAuth middleware

## Summary
Severity: Medium
Advisory: GHSA-6x2q-h3cr-8j2h
CVE: CVE-2026-41263
CWE: CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-6x2q-h3cr-8j2h
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-rc.2
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta1 <3.6.14
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.43
- Go: `github.com/traefik/traefik` — affected >=0

## Details
## Summary

There is a timing side-channel vulnerability in Traefik's BasicAuth middleware that allows an attacker to enumerate valid usernames through response-time differences.

The variable intended to hold a constant-time fallback secret always resolves to an empty string, causing the constant-time comparison to short-circuit in microseconds rather than performing a full bcrypt evaluation. This restores the original timing oracle and makes it possible to distinguish existing users from non-existing ones by measuring authentication response times.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2

## For more information

If there are any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

# BasicAuth Timing Regression: CVE-2026-32595 Fix Is a No-Op Due to Map Key/Value Confusion

## TL;DR

The patch for CVE-2026-32595 is a no-op. Line 49 of `basic_auth.go` has a
map key/value confusion that makes `notFoundSecret` always `""`. The
"constant time" fallback calls `goauth.CheckSecret(password, "")`, which
fast-fails in ~1us instead of running bcrypt (~60ms).

## Evidence (HEAD `786f7192e`, 2026-04-09)

Black-box PoC against live traefik binary on port 28080:

| bucket                       | n   | median   | min      |
|------------------------------|-----|----------|----------|
| existing user (wrong pw)     | 240 | 62.85 ms | 57.54 ms |
| nonexistent user (wrong pw)  | 400 |  0.48 ms |  0.35 ms |

Median ratio: **130.4x**. Classification: **8/8 correct**.

Go in-tree test: `goauth.CheckSecret` direct ratio **12,746x**.

## Root cause (4-step trace)

1. `basic_auth.go:49`: `users[slices.Collect(maps.Values(users))[0]]` -- looks
   up a hash as a username key, returns `""`.
2. `basic_auth.go:119-120`: calls `goauth.CheckSecret(password, "")`.
3. `go-http-auth/basic.go:87`: empty string matches no prefix, falls to default
   `compareMD5HashAndPassword`.
4. `basic.go:107-109`: `bytes.SplitN("", "$", 4)` returns length 1, function
   returns instantly.

## Files

- `poc/exploit.py` -- black-box Python timing oracle
- `poc/basic_auth_timing_regression_test.go` -- Go in-tree test
- `poc/traefik.yml` + `poc/dynamic.yml` -- traefik config
- `poc/live_http_poc_output_head.txt` -- verbatim PoC output on HEAD


Koda Reef

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-6x2q-h3cr-8j2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-41263
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.43
- https://github.com/traefik/traefik/releases/tag/v3.6.14
- https://github.com/traefik/traefik/releases/tag/v3.7.0-rc.2
