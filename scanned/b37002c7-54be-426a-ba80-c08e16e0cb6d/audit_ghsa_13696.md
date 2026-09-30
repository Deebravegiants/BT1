# [M] cordova-plugin-fingerprint-aio DoS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7vfx-hfvm-rhr8
CVE: CVE-2021-43849
CWE: CWE-617
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-02
Source: https://github.com/advisories/GHSA-7vfx-hfvm-rhr8
Type: github-advisory

## Affected
- npm: `cordova-plugin-fingerprint-aio` — affected >=0 <5.0.1

## Details
## Summary:

Sending a specially crafted intent with an invalid/empty extras `de.niklasmerz.cordova.biometric.BiometricActivity` can cause the app to crash. sending the intent repeatedly can prevent the app using this plugin from working, resulting in a denial of service (DoS) condition.

## Impact

A 3rd party app/remote attacker can exploit this vulnerability by sending a malicious intent to the target device, causing the app using this plugin from working to crash or become unresponsive, resulting in a denial of service (DoS) condition.

## Mitigation

Version 5.0.1 of the cordova-plugin-fingerprint-aio doesn't export the activity anymore and is no longer vulnerable.

If you want to fix older versions change the attribute `android:exported` of this code snippet in plugin.xml to `false`:

```xml
<config-file target="AndroidManifest.xml" parent="application">
      <activity android:name="de.niklasmerz.cordova.biometric.BiometricActivity" android:theme="@style/TransparentTheme" android:exported="false"/>
</config-file>
``` 

## Patches

Please upgrade to version 5.0.1 as soon as possible.

Please check out the release on [GitHub](https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio/releases/tag/v5.0.1).

## For more information
If you have any questions or comments about this advisory please go to the discussion on [GitHub](https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio/discussions/394).

## References
- https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio/security/advisories/GHSA-7vfx-hfvm-rhr8
- https://nvd.nist.gov/vuln/detail/CVE-2021-43849
- https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio/commit/27434a240f97f69fd930088654590c8ba43569df
- https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio
- https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio/discussions/394
- https://github.com/NiklasMerz/cordova-plugin-fingerprint-aio/releases/tag/v5.0.1
