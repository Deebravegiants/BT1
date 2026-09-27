# [C] CVE-2025-49655

## Summary
Severity: Critical
Advisory: CVE-2025-49655
Aliases: GHSA-cvhh-q5g5-qprp, PYSEC-2026-368
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/CVE-2025-49655
Type: osv

## Details
Deserialization of untrusted data can occur in versions of the Keras framework running versions 3.11.0 up to but not including 3.11.3, enabling a maliciously uploaded Keras file containing a TorchModuleWrapper class to run arbitrary code on an end user’s system when loaded despite safe mode being enabled. The vulnerability can be triggered through both local and remote files.

## References
- https://hiddenlayer.com/sai_security_advisor/2025-10-keras/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49655.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49655
- https://github.com/keras-team/keras/pull/21575
- https://github.com/keras-team/keras
