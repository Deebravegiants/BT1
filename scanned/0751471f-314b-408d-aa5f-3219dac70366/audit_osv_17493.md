# [M] CVE-2020-15509

## Summary
Severity: Medium
Advisory: CVE-2020-15509
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-15509
Type: osv

## Details
Nordic Semiconductor Android BLE Library through 2.2.1 and DFU Library through 1.10.4 for Android (as used by nRF Connect and other applications) can engage in unencrypted communication while showing the user that the communication is purportedly encrypted. The problem is in bond creation (e.g., internalCreateBond in BleManagerHandler).

## References
- https://github.com/NordicSemiconductor/Android-BLE-Library/commits/master
- https://github.com/NordicSemiconductor/Android-DFU-Library/commits/release
- https://secretdiary.ninja/index.php/2020/07/03/norec-attack-stripping-ble-encryption-from-nordicsemis-android-library-cve-2020-15509/
