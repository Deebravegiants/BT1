# [H] CVE-2024-48336

## Summary
Severity: High
Advisory: CVE-2024-48336
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-04
Source: https://osv.dev/vulnerability/CVE-2024-48336
Type: osv

## Details
The install() function of ProviderInstaller.java in Magisk App before canary version 27007 does not verify the GMS app before loading it, which allows a local untrusted app with no additional privileges to silently execute arbitrary code in the Magisk app and escalate privileges to root via a crafted package, aka Bug #8279. User interaction is not needed for exploitation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48336.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48336
- https://github.com/topjohnwu/Magisk/commit/c2eb6039579b8a2fb1e11a753cea7662c07bec02
- https://github.com/canyie/MagiskEoP
