# [C] Dumb Drop has an arbitrary file overwrite and path traversal for root shell

## Summary
Severity: Critical
Advisory: CVE-2025-24891
Aliases: GHSA-24f2-fv38-3274
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-24891
Type: osv

## Details
Dumb Drop is a file upload application. Users with permission to upload to the service are able to exploit a path traversal vulnerability to overwrite arbitrary system files. As the container runs as root by default, there is no limit to what can be overwritten. With this, it's possible to inject malicious payloads into files ran on schedule or upon certain service actions. As the service is not required to run with authentication enabled, this may permit wholly unprivileged users root access. Otherwise, anybody with a PIN.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24891.json
- https://github.com/DumbWareio/DumbDrop/security/advisories/GHSA-24f2-fv38-3274
- https://nvd.nist.gov/vuln/detail/CVE-2025-24891
- https://github.com/DumbWareio/DumbDrop/commit/cb586316648ccbfb21d27b84e90d72ccead9819d
