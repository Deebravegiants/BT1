# [M] Home Assistant MCP Server: YAML config backups written under www/ are served unauthenticated at /local/

## Summary
Severity: Medium
Advisory: GHSA-g39v-cvjh-8fpf
CWE: CWE-552
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-g39v-cvjh-8fpf
Type: github-advisory

## Affected
- PyPI: `ha-mcp` — affected >=0 <7.5.0

## Details
### Summary

When `ENABLE_YAML_CONFIG_EDITING=true`, every `ha_config_set_yaml` call backs up the pre-edit file to `<config>/www/yaml_backups/`, which Home Assistant serves at `/local/` with **no authentication**. Anyone who can reach the HA web interface can download the most recent pre-edit `configuration.yaml` (or other YAML file) — typically containing plaintext MQTT passwords, REST credentials, webhook IDs, geofence coordinates, and `shell_command` definitions — with zero credentials.

### Details

The backup feature is good — `do_backup` defaults to `True` and protects users from a bad edit. The issue is the location:

- `custom_components/ha_mcp_tools/__init__.py:596` — `backup_dir = config_dir / "www" / "yaml_backups"`
- `custom_components/ha_mcp_tools/__init__.py:602` — `backup_file = backup_dir / f"{safe_name}.{timestamp}.bak"`
- `custom_components/ha_mcp_tools/__init__.py:606-607,692-693` — backup path returned to caller and logged at INFO

`<config>/www/` is `/local/` and HA serves it unauthenticated by design (intended for static dashboard assets). An attacker discovers the path three ways: (1) it's returned to the MCP client in `result["backup_path"]`; (2) it's logged at INFO and recoverable via `ha_get_logs`; (3) the timestamp format is `%Y%m%d_%H%M%S` — 86,400 candidates per day, enumerable. Backups accumulate (no rotation), so a long-running install holds a chronological history.

**Preconditions:** `ENABLE_YAML_CONFIG_EDITING=true` (off by default), at least one YAML edit made, and the attacker can reach HA's port 8123 (LAN, or internet via Nabu Casa / reverse proxy).

### PoC

A pytest E2E test against a fresh Docker HA container with the custom component installed (using the project's existing `ha_container_with_fresh_config` fixture):

```
[1] ha_config_set_yaml(yaml_path="template", action="add", ...) → success=True
[1] backup_path = 'www/yaml_backups/configuration.yaml.20260505_171335.bak'
[2] GET http://<ha>:8123/local/yaml_backups/configuration.yaml.20260505_171335.bak
    (no Authorization header)
[2] HTTP 200, 440 bytes — the full pre-edit configuration.yaml
[control] GET /api/config without auth → HTTP 401
```

The control proves the result is meaningful: the same instance returns 401 for an authenticated endpoint; only `/local/` is unauthenticated by HA design.

### Impact

CWE-552 (Files or Directories Accessible to External Parties). Affects users with `ENABLE_YAML_CONFIG_EDITING=true` who have made at least one YAML edit. Anyone who can reach HA port 8123 reads the most recent pre-edit config without credentials. CVSS 6.5 medium (`AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`); 7.5 high if HA is internet-exposed.

### Resolution

Fixed in `7.4.1.dev456` (PR #1180). The fix relocates new backups to `<config>/.ha_mcp_tools_backups/` (config root, not served by `/local/`) and adds a one-time migration on integration setup that moves any pre-existing exposed backups, surfaces a persistent notification telling the user to rotate exposed secrets, and removes the legacy directory if empty.

The fix ships in the next biweekly stable release and is available immediately on the dev channel. Updating to a release containing the fix is sufficient — no manual action required for users who upgrade.

### Manual cleanup (for users who cannot upgrade yet)

If you used `ha_config_set_yaml` on a vulnerable version and cannot wait for the next stable release, manually remove the exposed backups:

```
rm -rf <config>/www/yaml_backups/
```

Then rotate any secrets that may have been in the YAML files those backups captured (MQTT/REST credentials, webhook IDs, `shell_command` definitions, geofence coordinates). The directory is reachable at `http(s)://<ha-host>:8123/local/yaml_backups/` until removed. After the next addon/package upgrade containing the fix, the integration will run this cleanup automatically and surface a persistent notification with the same rotation guidance.

## References
- https://github.com/homeassistant-ai/ha-mcp/security/advisories/GHSA-g39v-cvjh-8fpf
- https://github.com/homeassistant-ai/ha-mcp/pull/1180
- https://github.com/homeassistant-ai/ha-mcp/commit/09c524526b5f945638aa97de6218fadcd233023c
- https://github.com/homeassistant-ai/ha-mcp
- https://github.com/homeassistant-ai/ha-mcp/releases/tag/v7.4.1.dev456
- https://github.com/homeassistant-ai/ha-mcp/releases/tag/v7.5.0
