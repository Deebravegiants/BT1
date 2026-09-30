# [M] CVE-2024-25742

## Summary
Severity: Medium
Advisory: CVE-2024-25742
CVSS: 6.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-25742
Type: osv

## Details
In the Linux kernel before 6.9, an untrusted hypervisor can inject virtual interrupt 29 (#VC) at any point in time and can trigger its handler. This affects AMD SEV-SNP and AMD SEV-ES.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=e3ef461af35a8c74f2f4ce6616491ddb355a208f
- https://www.amd.com/en/resources/product-security/bulletin/amd-sb-3008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25742.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25742
- https://github.com/torvalds/linux/commit/e3ef461af35a8c74f2f4ce6616491ddb355a208f
