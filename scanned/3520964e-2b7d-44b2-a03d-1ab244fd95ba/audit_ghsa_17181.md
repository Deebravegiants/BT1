# [H] SSRF Vulnerability on assetlinks_check(act_name, well_knowns)

## Summary
Severity: High
Advisory: GHSA-wfgj-wrgh-h3r3
CVE: CVE-2024-29190
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-wfgj-wrgh-h3r3
Type: github-advisory

## Affected
- PyPI: `mobsfscan` — affected >=0 <0.3.8

## Details
### Summary
While examining the "App Link assetlinks.json file could not be found" vulnerability detected by MobSF, we, as the Trendyol Application Security team, noticed that a GET request was sent to the "/.well-known/assetlinks.json" endpoint for all hosts written with "android:host". In the AndroidManifest.xml file.

Since MobSF does not perform any input validation when extracting the hostnames in "android:host", requests can also be sent to local hostnames. This may cause SSRF vulnerability.

### Details
Example <intent-filter structure in AndroidManifest.xml:

```
<intent-filter android:autoVerify="true">
<action android:name="android.intent.action.VIEW" />
<category android:name="android.intent.category.DEFAULT" />
<category android:name="android.intent.category.BROWSABLE" />
<data android:host="192.168.1.102/user/delete/1#" android:scheme="http" />
</intent-filter>
```


We defined it as android:host="192.168.1.102/user/delete/1#". Here, the "#" character at the end of the host prevents requests from being sent to the "/.well-known/assetlinks.json" endpoint and ensures that requests are sent to the endpoint before it.


<img width="617" alt="image" src="https://github.com/MobSF/Mobile-Security-Framework-MobSF/assets/150332295/c570cb00-e947-4ad7-af80-26d46c0ad3f7">


### PoC
https://drive.google.com/file/d/1nbKMd2sKosbJef5Mh4DxjcHcQ8Hw0BNR/view?usp=share_link


### Impact
The attacker can cause the server to make a connection to internal-only services within the organization's infrastructure.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-wfgj-wrgh-h3r3
- https://nvd.nist.gov/vuln/detail/CVE-2024-29190
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/5a8eeee73c5f504a6c3abdf2a139a13804efdb77
- https://github.com/MobSF/mobsfscan/commit/61fd40b477bbf9d204eb8c5a83a86c396d839798
- https://github.com/MobSF/mobsfscan/commit/cd01b71770a6e56c1c71b0e5f454e7b6c9c64ef4
- https://drive.google.com/file/d/1nbKMd2sKosbJef5Mh4DxjcHcQ8Hw0BNR/view?usp=share_link
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/pypa/advisory-database/tree/main/vulns/mobsf/PYSEC-2024-257.yaml
