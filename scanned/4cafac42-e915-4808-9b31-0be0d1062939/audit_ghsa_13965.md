# [M] Helm vulnerable to information disclosure via getHostByName Function 

## Summary
Severity: Medium
Advisory: GHSA-pwcw-6f5g-gxf8
CVE: CVE-2023-25165
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-pwcw-6f5g-gxf8
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=3.0.0 <3.11.1

## Details
A Helm contributor discovered an information disclosure vulnerability using the `getHostByName` template function.

### Impact

`getHostByName` is a Helm template function introduced in Helm v3. The function is able to accept a hostname and return an IP address for that hostname. To get the IP address the function performs a DNS lookup. The DNS lookup happens when used with `helm install|upgrade|template` or when the Helm SDK is used to render a chart.

Information passed into the chart can be disclosed to the DNS servers used to lookup the IP address. For example, a malicious chart could inject `getHostByName` into a chart in order to disclose values to a malicious DNS server.

### Patches

The issue has been fixed in Helm 3.11.1.

### Workarounds

Prior to using a chart with Helm verify the `getHostByName` function is not being used in a template to disclose any information you do not want passed to DNS servers.

### For more information

Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits

Disclosed by Philipp Stehle at SAP.

## References
- https://github.com/helm/helm/security/advisories/GHSA-pwcw-6f5g-gxf8
- https://nvd.nist.gov/vuln/detail/CVE-2023-25165
- https://github.com/helm/helm/commit/293b50c65d4d56187cd4e2f390f0ada46b4c4737
- https://github.com/helm/helm/commit/5abcf74227bfe8e5a3dbf105fe62e7b12deb58d2
- https://github.com/helm/helm
- https://pkg.go.dev/vuln/GO-2023-1547
