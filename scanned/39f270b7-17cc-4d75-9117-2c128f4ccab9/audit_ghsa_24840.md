# [M] Rancher Login Parameter Can Be Edited

## Summary
Severity: Medium
Advisory: GHSA-2p4g-jrmx-r34m
CVE: CVE-2019-11881
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2p4g-jrmx-r34m
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=0

## Details
A vulnerability exists in Rancher 2.1.4 in the login component, where the `errorMsg` parameter can be tampered to display arbitrary content, filtering tags but not special characters or symbols. There's no other limitation of the message, allowing malicious users to lure legitimate users to visit phishing sites with scare tactics, e.g., displaying a "This version of Rancher is outdated, please visit https://malicious.rancher.site/upgrading" message.

**PoC**
1. Access the following endpoint on any Rancher instance up to 2.1.4: `https://RANCHER:PORT/login?errorMsg=%68%74%74%70%73%3a%2f%2f%77%77%77%2e%6f%77%61%73%70%2e%6f%72%67%2f%69%6e%64%65%78%2e%70%68%70%2f%57%65%62%5f%50%61%72%61%6d%65%74%65%72%5f%54%61%6d%70%65%72%69%6e%67`

It will display a [link](https://www.owasp.org/index.php/Web_Parameter_Tampering) to OWASP Wiki explaining Web Parameter Tampering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11881
- https://github.com/rancher/rancher/issues/20216
- https://github.com/rancher/rancher/commit/e59adbc7565251919d84d6e353421104be8da06e
- https://github.com/MauroEldritch/VanCleef
- https://github.com/rancher/rancher
- https://github.com/rancher/rancher/blob/v2.2.4/pkg/auth/providers/saml/saml_client.go#L282
