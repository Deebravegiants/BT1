# [M] Potential HTTP policy bypass when using header rules in Cilium

## Summary
Severity: Medium
Advisory: GHSA-2h44-x2wx-49f4
CVE: CVE-2023-30851
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-2h44-x2wx-49f4
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=0 <1.11.16
- Go: `github.com/cilium/cilium` — affected >=1.12.0 <1.12.9
- Go: `github.com/cilium/cilium` — affected >=1.13.0 <1.13.2

## Details
### Impact

This issue only impacts users who:

- Have a HTTP policy that applies to multiple `toEndpoints` AND
- Have an allow-all rule in place that affects only one of those endpoints

In such cases, a wildcard rule will be appended to the set of HTTP rules, which could cause bypass of HTTP policies.

### Patches

This issue has been patched in Cilium 1.11.16, 1.12.9, and 1.13.2.

### Workarounds

Rewrite HTTP rules for each endpoint separately. For example, if the initial rule looks like:

```
  egress:
    - toEndpoints:
        - matchLabels:
            k8s:kind: echo
        - matchLabels:
            k8s:kind: example
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET"
```

It should be rewritten to:
 
```
  egress:
    - toEndpoints:
        - matchLabels:
            k8s:kind: echo
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET"
    - toEndpoints:
        - matchLabels:
            k8s:kind: example
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET"
```     

### Acknowledgements

The Cilium community has worked together with members of Isovalent to prepare these mitigations. Special thanks to @jrajahalme for investigating and fixing the issue.

### For more information

If you have any questions or comments about this advisory, please reach out on [Slack](https://docs.cilium.io/en/latest/community/community/#slack).

As usual, if you think you found a related vulnerability, we strongly encourage you to report security vulnerabilities to our private security mailing list: [security@cilium.io](mailto:security@cilium.io) - first, before disclosing them in any public forums. This is a private mailing list where only members of the Cilium internal security team are subscribed to, and is treated as top priority.

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-2h44-x2wx-49f4
- https://nvd.nist.gov/vuln/detail/CVE-2023-30851
- https://github.com/cilium/cilium
- https://github.com/cilium/cilium/releases/tag/v1.11.16
- https://github.com/cilium/cilium/releases/tag/v1.12.9
- https://github.com/cilium/cilium/releases/tag/v1.13.2
