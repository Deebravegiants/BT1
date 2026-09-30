# [C] Nix affected by unsafe NAR unpacking

## Summary
Severity: Critical
Advisory: CVE-2024-45593
Aliases: GHSA-h4vv-h3jq-v493
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/CVE-2024-45593
Type: osv

## Details
Nix is a package manager for Linux and other Unix systems. A bug in Nix 2.24 prior to 2.24.6 allows a substituter or malicious user to craft a NAR that, when unpacked by Nix, causes Nix to write to arbitrary file system locations to which the Nix process has access. This will be with root permissions when using the Nix daemon. This issue is fixed in Nix 2.24.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45593.json
- https://github.com/NixOS/nix/security/advisories/GHSA-h4vv-h3jq-v493
- https://nvd.nist.gov/vuln/detail/CVE-2024-45593
- https://github.com/NixOS/nix/commit/eb11c1499876cd4c9c188cbda5b1003b36ce2e59
