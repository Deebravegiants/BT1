# [H] Infinite loop condition in Amazon.IonDotnet

## Summary
Severity: High
Advisory: GHSA-gm2p-wf5c-w3pj
CVE: CVE-2025-3857
CWE: CWE-502, CWE-835
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-21
Source: https://github.com/advisories/GHSA-gm2p-wf5c-w3pj
Type: github-advisory

## Affected
- NuGet: `Amazon.IonDotnet` — affected >=0 <1.3.1

## Details
## Summary

[Amazon.IonDotnet (ion-dotnet)](https://github.com/amazon-ion/ion-dotnet) is a .NET library with an implementation of the [Ion data serialization format](https://amazon-ion.github.io/ion-docs/).

An issue exists in Amazon.IonDotnet and the RawBinaryReader class where, under certain conditions, an actor could trigger an infinite loop condition.

## Impact

When reading binary Ion data through Amazon.IonDotnet using the RawBinaryReader class, Amazon.IonDotnet does not check the number of bytes read from the underlying stream while deserializing the binary format. If the Ion data is malformed or truncated, this triggers an infinite loop condition that could potentially result in a denial of service.

**Impacted versions: <=1.3.0**

## Patches

This issue has been addressed in Amazon.IonDotnet version [1.3.1](https://github.com/amazon-ion/ion-dotnet/releases/tag/v1.3.1). We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

## Workarounds

There are no workarounds. Upgrade to version 1.3.1.

## References

If you have any questions or comments about this advisory, contact AWS/Amazon Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## Credit

We would like to thank Josh Coleman from Symbotic for collaborating on this issue through the coordinated vulnerability disclosure process.

## References
- https://github.com/amazon-ion/ion-dotnet/security/advisories/GHSA-gm2p-wf5c-w3pj
- https://nvd.nist.gov/vuln/detail/CVE-2025-3857
- https://github.com/amazon-ion/ion-dotnet/commit/34a4f5215eceac1bb7bf434c4f2310d64d1b703b
- https://aws.amazon.com/security/security-bulletins/AWS-2025-009
- https://github.com/amazon-ion/ion-dotnet
- https://github.com/amazon-ion/ion-dotnet/releases/tag/v1.3.1
