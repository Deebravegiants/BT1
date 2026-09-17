# [M] NutzBoot Incorrect Privilege Assignment vulnerability

## Summary
Severity: Medium
Advisory: GHSA-53v5-9752-qq92
CVE: CVE-2025-13806
CWE: CWE-266, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-01
Source: https://github.com/advisories/GHSA-53v5-9752-qq92
Type: github-advisory

## Affected
- Maven: `org.nutz:nutzboot-parent` — affected >=0

## Details
A security vulnerability has been detected in nutzam NutzBoot up to 2.6.0-SNAPSHOT. This impacts an unknown function of the file nutzboot-demo/nutzboot-demo-simple/nutzboot-demo-simple-web3j/src/main/java/io/nutz/demo/simple/module/EthModule.java of the component Transaction API. The manipulation of the argument from/to/wei leads to improper authorization. Remote exploitation of the attack is possible. The exploit has been disclosed publicly and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-13806
- https://github.com/Xzzz111/exps/blob/main/archives/nutzboot-UnauthorizedTransfer-1/report.md
- https://github.com/Xzzz111/exps/blob/main/archives/nutzboot-UnauthorizedTransfer-1/report.md#vulnerability-details-and-poc
- https://github.com/nutzam/nutzboot
- https://vuldb.com/?ctiid.333816
- https://vuldb.com/?id.333816
- https://vuldb.com/?submit.692061
