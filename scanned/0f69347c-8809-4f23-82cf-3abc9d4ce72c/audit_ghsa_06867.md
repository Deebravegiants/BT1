# [C] Wings exposes node configuration secrets through egg configuration-file templating

## Summary
Severity: Critical
Advisory: GHSA-pfvc-3p5h-x7h6
CVE: CVE-2026-52855
CWE: CWE-200, CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-pfvc-3p5h-x7h6
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.12.3

## Details
### Impact

**Type:** Exposure of sensitive information / insufficiently protected credentials
leading to privilege escalation and full node compromise.

Wings exposes its **entire** daemon configuration to the egg configuration-file
templating engine. When Wings renders a server's configuration files, any
`{{config.<path>}}` placeholder in a replacement value is resolved against the
full marshalled daemon configuration, with no restriction on which paths may be
read.

Because the Panel substitutes **user-controlled** egg variable values into these
replacements before sending them to Wings, a low-privileged user can smuggle a
`{{config.*}}` placeholder through a variable value. The placeholder is then
resolved by Wings and written into a file inside the user's own server, where it
can be read via the file manager or SFTP.

This allows reading, among other values:

- `{{config.token}}` - the node's daemon token, which is both the API bearer for
  the Panel⇆Wings channel **and** the HMAC signing key for every JWT the node
  issues;
- `{{config.token_id}}`;
- `{{config.docker.registries}}` - configured container-registry credentials.

**Who is impacted:** Any deployment where a user who is not fully trusted can set
an egg variable value (e.g. a server owner or a subuser with the `startup.update`
permission) **and** the server's egg renders a user-editable variable into a
configuration file via `{{server.build.env.*}}`. This pattern is common across
stock and community eggs, so most multi-tenant / shared-hosting deployments are
affected.

**Resulting impact:** Disclosure of the node daemon token lets the attacker forge
authentication tokens and act against **every server on that node**, a full-node compromise reachable from a low-privileged
account.

### Patches

Yes. Fixed in **Wings `v1.12.3`** (Panel is unaffected; the fix is Wings-only).

Wings no longer exposes its full configuration to the templating engine only an
explicit, non-secret subset (the Docker network interface) can be resolved by
`{{config.*}}` placeholders.

Users should upgrade Wings to `v1.12.3` or later.

**After upgrading, rotate the affected nodes' daemon tokens**, since a previously
exfiltrated token remains valid until rotated (Admin → Nodes → Configuration →
reset the token, then re-deploy `config.yml` to the node).

### Workarounds

For operators who cannot upgrade immediately:

- Audit your eggs and ensure no **user-editable** variable is rendered into a
  configuration file, or mark such variables non-editable.

These reduce exposure but are not a complete fix; upgrading Wings is the
recommended action.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-pfvc-3p5h-x7h6
- https://github.com/pterodactyl/wings/commit/eb65e27ae077a63e38518c490768486af1cd86a9
- https://github.com/pterodactyl/wings
- https://github.com/pterodactyl/wings/releases/tag/v1.12.3
