# [M] Denial of service in Helm

## Summary
Severity: Medium
Advisory: BIT-helm-2022-36055
Aliases: CVE-2022-36055, GHSA-7hfp-qfw3-5jxh, GO-2022-0962
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-helm-2022-36055
Type: osv

## Affected
- Bitnami: `helm` — affected >=3.0.0 <3.9.4

## Details
Helm is a tool for managing Charts. Charts are packages of pre-configured Kubernetes resources. Fuzz testing, provided by the CNCF, identified input to functions in the _strvals_ package that can cause an out of memory panic. The _strvals_ package contains a parser that turns strings in to Go structures. The _strvals_ package converts these strings into structures Go can work with. Some string inputs can cause array data structures to be created causing an out of memory panic. Applications that use the _strvals_ package in the Helm SDK to parse user supplied input can suffer a Denial of Service when that input causes a panic that cannot be recovered from. The Helm Client will panic with input to `--set`, `--set-string`, and other value setting flags that causes an out of memory panic. Helm is not a long running service so the panic will not affect future uses of the Helm client. This issue has been resolved in 3.9.4. SDK users can validate strings supplied by users won't create large arrays causing significant memory usage before passing them to the _strvals_ functions.

## References
- https://github.com/helm/helm/releases/tag/v3.9.4
- https://github.com/helm/helm/security/advisories/GHSA-7hfp-qfw3-5jxh
- https://nvd.nist.gov/vuln/detail/CVE-2022-36055
