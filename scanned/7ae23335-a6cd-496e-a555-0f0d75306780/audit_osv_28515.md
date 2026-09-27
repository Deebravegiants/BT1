# [H] CVE-2024-33904

## Summary
Severity: High
Advisory: CVE-2024-33904
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-29
Source: https://osv.dev/vulnerability/CVE-2024-33904
Type: osv

## Details
In plugins/HookSystem.cpp in Hyprland through 0.39.1 (before 28c8561), through a race condition, a local attacker can cause execution of arbitrary assembly code by writing to a predictable temporary file.

## References
- https://www.openwall.com/lists/oss-security/2024/04/28/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/33xxx/CVE-2024-33904.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-33904
- https://github.com/hyprwm/Hyprland/issues/5787
- https://github.com/hyprwm/Hyprland/commit/28c85619243e6320e75d7abcfe8244fa99d054dd
