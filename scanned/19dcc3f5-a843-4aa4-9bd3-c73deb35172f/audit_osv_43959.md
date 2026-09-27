# [C] AzuraCast through 0.23.8 Liquidsoap Configuration Write via Profile Edit Serialization Group Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-76836
Aliases: GHSA-q8wg-3qg7-8pc7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76836
Type: osv

## Details
AzuraCast exposes the Liquidsoap custom configuration fields through an endpoint that does not require the permission guarding them. The backend_config property in backend/src/Entity/Station.php is annotated with GROUP_GENERAL, and PUT /api/station/{station_id}/profile/edit in backend/src/Controller/Api/Stations/ProfileEditController.php deserializes with that group while requiring only StationPermissions::Profile. AbstractArrayEntity::fromArray() then assigns every public property with no field-level permission check, so custom_config_top, custom_config, custom_config_pre_playlists, custom_config_pre_live, custom_config_pre_fade and custom_config_bottom are writable through it. ConfigWriter::writeCustomConfigurationSection() emits those values verbatim into the generated Liquidsoap .liq script, where the process.run() and process.exec() built-ins execute operating system commands when the backend restarts, which the built-in sync task triggers automatically once needs_restart is set. The dedicated endpoint for the same data, PUT /api/station/{id}/liquidsoap-config, requires StationPermissions::Broadcasting, so a station manager holding only the profile permission reaches configuration that the intended boundary reserves for broadcasting operators.

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-q8wg-3qg7-8pc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76836.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76836
- https://www.vulncheck.com/advisories/azuracast-through-liquidsoap-configuration-write-via-profile-edit-serialization-group-bypass
- https://github.com/AzuraCast/AzuraCast
- https://github.com/AzuraCast/AzuraCast/blob/0.23.8/backend/src/Entity/Station.php
- https://github.com/AzuraCast/AzuraCast/blob/0.23.8/backend/src/Radio/Backend/Liquidsoap/ConfigWriter.php
