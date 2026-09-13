# [H] Hugo: security.http.urls deny rules bypassed by alternate IPv4 encodings (SSRF)

## Summary
Severity: High
Advisory: GHSA-r46f-3rpw-hxrv
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-r46f-3rpw-hxrv
Type: github-advisory

## Affected
- Go: `github.com/gohugoio/hugo` — affected >=0.162.0 <0.163.1

## Details
### Impact

  The default `security.http.urls` policy denies requests to loopback, internal,
  and cloud-metadata IPv4 literals (e.g. `http://127.0.0.1/`,
  `http://169.254.169.254/`). The deny rule only matched dotted-decimal notation,
  so alternate IPv4 encodings of the same addresses — integer, hex, or octal,
  which contain no dot — passed the policy:

  - `http://2130706433/` → `127.0.0.1`
  - `http://2852039166/` → `169.254.169.254` (cloud metadata)
  - `http://0x7f000001/`, `http://017700000001/`, `http://0/`

  When a template passes an untrusted or data-derived URL to
  `resources.GetRemote` and the host platform uses the
  cgo system resolver, these encodings resolve to the blocked address — allowing
  build-time server-side requests to loopback and internal services, including the
  cloud-metadata endpoint in hosted/CI builds. The same check is reused on
  redirects, so the gap also applies to each redirect hop.

  This affects sites that rely on `security.http.urls` as a security boundary
  while fetching attacker-influenced remote URLs; it does not affect sites that
  fully trust the URLs they fetch.

  ### Patches

  Fixed in **v0.163.1**. Integer/hex/octal IPv4 hosts are now canonicalized to
  dotted-decimal before the policy is applied, so every encoding of an address is
  treated alike. No configuration change is required.

  ### Workarounds

  Avoid passing untrusted URLs to `resources.GetRemote`, or
  tighten `security.http.urls` to an explicit allow-list of trusted hosts.

  ### Affected versions

  v0.162.0 – v0.163.0 (patched in v0.163.1).

## References
- https://github.com/gohugoio/hugo/security/advisories/GHSA-r46f-3rpw-hxrv
- https://github.com/gohugoio/hugo
