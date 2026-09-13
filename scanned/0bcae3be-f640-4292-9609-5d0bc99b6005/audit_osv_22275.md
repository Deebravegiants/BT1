# [C] Remote Command Injection in RaspberryMatic

## Summary
Severity: Critical
Advisory: CVE-2022-24796
Aliases: GHSA-g7vv-7rmf-mff7
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-31
Source: https://osv.dev/vulnerability/CVE-2022-24796
Type: osv

## Details
RaspberryMatic is a free and open-source operating system for running a cloud-free smart-home using the homematicIP / HomeMatic hardware line of IoT devices. A Remote Code Execution (RCE) vulnerability in the file upload facility of the WebUI interface of RaspberryMatic exists. Missing input validation/sanitization in the file upload mechanism allows remote, unauthenticated attackers with network access to the WebUI interface to achieve arbitrary operating system command execution via shell metacharacters in the HTTP query string. Injected commands are executed as root, thus leading to a full compromise of the underlying system and all its components. Versions after `2.31.25.20180428` and prior to `3.63.8.20220330` are affected. Users are advised to update to version `3.63.8.20220330` or newer. There are currently no known workarounds to mitigate the security impact and users are advised to update to the latest version available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24796.json
- https://github.com/jens-maus/RaspberryMatic/security/advisories/GHSA-g7vv-7rmf-mff7
- https://nvd.nist.gov/vuln/detail/CVE-2022-24796
- https://github.com/jens-maus/RaspberryMatic/commit/34854659a63e9fb3ad529bb413e96978c6450a53
