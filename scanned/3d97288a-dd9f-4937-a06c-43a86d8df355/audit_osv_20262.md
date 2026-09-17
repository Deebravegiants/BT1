# [H] CVE-2021-32646

## Summary
Severity: High
Advisory: CVE-2021-32646
Aliases: GHSA-3f73-8j6q-28v8
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-32646
Type: osv

## Details
Roomer is a discord bot cog (extension) which provides automatic voice channel generation as well as private voice and text channels. A vulnerability has been discovered allowing discord users to get the ``manage channel`` permissions in a private VC they have joined. This allowed them to make changes to or delete the voice channel they have taken over. The exploit does not allow access or control to any other channels in the server. Upgrade to version 1.0.1 for a patched version of the cog. As a workaround you may disable private VCs in your guild(server) or unload the roomer cog to render the exploit unusable.

## References
- https://github.com/Dav-Git/Dav-Cogs/commit/fbe2ae8ec851a2e9e3e2370db3b812f268e8c8cb
- https://github.com/Dav-Git/Dav-Cogs/security/advisories/GHSA-3f73-8j6q-28v8
