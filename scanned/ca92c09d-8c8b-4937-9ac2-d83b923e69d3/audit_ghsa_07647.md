# [M] Caddy is vulnerable to cross-origin config application via local admin API /load 

## Summary
Severity: Medium
Advisory: GHSA-879p-475x-rqh2
CVE: CVE-2026-27589
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-879p-475x-rqh2
Type: github-advisory

## Affected
- Go: `github.com/caddyserver/caddy/v2` — affected >=0 <2.11.1

## Details
commit: e0f8d9b2047af417d8faf354b675941f3dac9891 (as-of 2026-02-04)
channel: GitHub security advisory (per SECURITY.md)

## summary

The local caddy admin API (default listen `127.0.0.1:2019`) exposes a state-changing `POST /load` endpoint that replaces the entire running configuration.

When origin enforcement is not enabled (`enforce_origin` not configured), the admin endpoint accepts cross-origin requests (e.g., from attacker-controlled web content in a victim browser) and applies an attacker-supplied JSON config. this can change the admin listener settings and alter HTTP server behavior without user intent.

## Severity

Medium

Justification:
- The attacker can apply an arbitrary caddy config (integrity impact) by driving a victim’s local admin API.
- Exploitation requires a victim running caddy with the admin API enabled and visiting an attacker-controlled page (or otherwise issuing the request from an untrusted local client).

## Affected component

- `caddyconfig/load.go: adminLoad.handleLoad` (`/load` admin endpoint)
- Pinned callsite: https://github.com/caddyserver/caddy/blob/e0f8d9b2047af417d8faf354b675941f3dac9891/caddyconfig/load.go#L73

## Reproduction

Attachment: `poc.zip` (integration harness) with canonical and control runs.

```bash
unzip -q -o poc.zip -d poc
cd poc/poc-F-CADDY-ADMIN-LOAD-001
make test
```

Expected output (excerpt):

```
[CALLSITE_HIT]: adminLoad.handleLoad
[PROOF_MARKER]: http_code=200 admin_moved=true response_pwned=true
```

Control output (excerpt):

```
[NC_MARKER]: http_code=403 load_blocked=true admin_moved=false response_pwned=false
```

## Impact

An attacker can replace the running caddy configuration via the local admin API. Depending on the deployed configuration/modules, this can:
- Change admin listener settings (e.g., move the admin listener to a new address)
- Change HTTP server behavior (e.g., alter routes/responses)

## Suggested remediation

Ensure cross-origin web content cannot trigger `POST /load` on the local admin API by default, for example by:
- Enabling origin enforcement by default for unsafe methods, and/or
- Requiring an unguessable token for `/load` (and other state-changing admin endpoints).

[poc.zip](https://github.com/user-attachments/files/25079818/poc.zip)
[PR_DESCRIPTION.md](https://github.com/user-attachments/files/25079820/PR_DESCRIPTION.md)

## References
- https://github.com/caddyserver/caddy/security/advisories/GHSA-879p-475x-rqh2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27589
- https://github.com/caddyserver/caddy/commit/65e0ddc22137bbbaa68c842ae0b98d0548504545
- https://github.com/caddyserver/caddy
- https://github.com/caddyserver/caddy/releases/tag/v2.11.1
- https://github.com/user-attachments/files/25079818/poc.zip
- https://github.com/user-attachments/files/25079820/PR_DESCRIPTION.md
- https://pkg.go.dev/vuln/GO-2026-4537
