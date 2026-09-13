# [H] OpenWrt vulnerable to local privilage escalation

## Summary
Severity: High
Advisory: CVE-2025-62525
Aliases: GHSA-h427-frpr-7cqr
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2025-10-22
Source: https://osv.dev/vulnerability/CVE-2025-62525
Type: osv

## Details
OpenWrt Project is a Linux operating system targeting embedded devices. Prior to version 24.10.4, local users could read and write arbitrary kernel memory using the ioctls of the ltq-ptm driver which is used to drive the datapath of the DSL line. This only effects the lantiq target supporting xrx200, danube and amazon SoCs from Lantiq/Intel/MaxLinear with the DSL in PTM mode. The DSL driver for the VRX518 is not affected. ATM mode is also not affected. Most VDSL lines use PTM mode and most ADSL lines use ATM mode. OpenWrt is normally running as a single user system, but some services are sandboxed. This vulnerability could allow attackers to escape a ujail sandbox or other contains. This is fixed in OpenWrt 24.10.4. There are no workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62525.json
- https://github.com/openwrt/openwrt/security/advisories/GHSA-h427-frpr-7cqr
- https://nvd.nist.gov/vuln/detail/CVE-2025-62525
- https://openwrt.org/advisory/2025-10-22-2
- https://github.com/openwrt/openwrt/commit/2a76abc5442e3f74d95b4caa9bb57e5488fc132e
- https://github.com/openwrt/openwrt/commit/e001b31163a77683ee741d169f794cfa50926f37
