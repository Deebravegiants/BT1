# [M] CVE-2020-36248

## Summary
Severity: Medium
Advisory: CVE-2020-36248
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-19
Source: https://osv.dev/vulnerability/CVE-2020-36248
Type: osv

## Details
The ownCloud application before 2.15 for Android allows attackers to use adb to include a PIN preferences value in a backup archive, and consequently bypass the PIN lock feature by restoring from this archive.

## References
- https://owncloud.com/security-advisories/bypassing-app-lock-pattern-passcode-fingerprint-lock-android-oc-sa-2020-003/
