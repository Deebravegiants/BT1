# [M] Improper Validation of Admin Key in PIV Smartcard

## Summary
Severity: Medium
Advisory: CVE-2025-25201
Aliases: GHSA-jfhm-ppq8-7hgx
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-25201
Type: osv

## Details
Nitrokey 3 Firmware is the the firmware of Nitrokey 3 USB keys. For release 1.8.0, and test releases with PIV enabled prior to 1.8.0, the PIV application could accept invalid keys for authentication of the admin key. This could lead to compromise of the integrity of the data stored in the application. An attacker without access to the proper administration key would be able to generate new keys and overwrite certificates. Such an attacker would not be able to read-out or extract existing private data, nor would they be able to gain access to cryptographic operations that would normally require PIN-based authentication. The issue is fixed in piv-authenticator 0.3.9, and in Nitrokey's firmware 1.8.1.

## References
- https://github.com/Nitrokey/nitrokey-3-firmware/releases/tag/v1.8.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25201.json
- https://github.com/Nitrokey/nitrokey-3-firmware/security/advisories/GHSA-jfhm-ppq8-7hgx
- https://nvd.nist.gov/vuln/detail/CVE-2025-25201
- https://www.nitrokey.com/blog/2025/nitrokey-3-firmware-v181-security-update
