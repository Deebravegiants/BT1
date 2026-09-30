# [H] User impersonation due to incorrect handling of the login JWT

## Summary
Severity: High
Advisory: GHSA-h77f-xxx7-4858
CVE: CVE-2021-39177
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-h77f-xxx7-4858
Type: github-advisory

## Affected
- Maven: `org.geysermc:connector` — affected >=0 <1.4.2-SNAPSHOT

## Details
### Impact
<!--_What kind of vulnerability is it? Who is impacted?_-->
This allows anyone that can connect to the server to forge a LoginPacket with manipulated JWT token allowing impersonation as any Bedrock user. Unless credentials are saved in your configuration, online mode is not affected as users are still required to log in separately. If your credentials are saved, there is no risk of exposing your email or password.

### Patches
<!--_Has the problem been patched? What versions should users upgrade to?_-->
This was patched as part of https://github.com/GeyserMC/Geyser/commit/b9541505af68ac7b7c093206ac7b1ba88957a5a6 and https://github.com/GeyserMC/Geyser/commit/ab2f5b326fe590e09167e8b45b4b165ac06ecd13. if your Geyser version is `1.4.2-SNAPSHOT` or later, the issue has been addressed on your build.

### Workarounds
<!--_Is there a way for users to fix or remediate the vulnerability without upgrading?_-->
Geyser strongly recommends updating to fix this issue. If this isn't possible:
- Use online mode and don't save credentials in your Geyser configuration
- Use an additional authentication method on the Java server

### References
<!--_Are there any links users can visit to find out more?_-->
This was disclosed to us by a staff member over at Hive; you can read their disclosure here: https://updates.playhive.com/weekend-maintenance-disclosure-2kJMaY

### For more information
If you have any questions or comments about this advisory:
* Come talk to us over on our [Discord](https://discord.gg/geysermc) server in the [#development](https://discord.com/channels/613163671870242838/613170125696270357) channel

## References
- https://github.com/GeyserMC/Geyser/security/advisories/GHSA-h77f-xxx7-4858
- https://nvd.nist.gov/vuln/detail/CVE-2021-39177
- https://github.com/GeyserMC/Geyser/commit/b9541505af68ac7b7c093206ac7b1ba88957a5a6
- https://github.com/GeyserMC/Geyser
- https://updates.playhive.com/weekend-maintenance-disclosure-2kJMaY
