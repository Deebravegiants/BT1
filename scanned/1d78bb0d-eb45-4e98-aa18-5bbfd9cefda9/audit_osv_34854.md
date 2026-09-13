# [M] CVE-2025-65835

## Summary
Severity: Medium
Advisory: CVE-2025-65835
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-65835
Type: osv

## Details
The Cordova plugin cordova-plugin-x-socialsharing (SocialSharing-PhoneGap-Plugin) for Android 6.0.4, registers an exported broadcast receiver nl.xservices.plugins.ShareChooserPendingIntent with an android.intent.action.SEND intent filter. The onReceive implementation accesses Intent.EXTRA_CHOSEN_COMPONENT without checking for null. If a broadcast is sent with extras present but without EXTRA_CHOSEN_COMPONENT, the code dereferences a null value and throws a NullPointerException. Because the receiver is exported and performs no permission or caller validation, any local application on the device can send crafted ACTION_SEND broadcasts to this component and repeatedly crash the host application, resulting in a local, unauthenticated application-level denial of service for any app that includes the plugin.

## References
- https://medium.com/@lcrawfqrd/local-dos-via-exported-receivers-f6b1da10d3b7
- https://www.npmjs.com/package/cordova-plugin-x-socialsharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65835.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65835
- https://github.com/EddyVerbruggen/SocialSharing-PhoneGap-Plugin
