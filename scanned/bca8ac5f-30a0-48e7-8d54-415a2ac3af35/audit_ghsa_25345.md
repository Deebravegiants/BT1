# [H] Improper Privilege Management in Cilium

## Summary
Severity: High
Advisory: GHSA-fmrf-gvjp-5j5g
CVE: CVE-2022-29179
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fmrf-gvjp-5j5g
Type: github-advisory

## Affected
- Go: `github.com/cilium/cilium` — affected >=1.11.0 <1.11.5
- Go: `github.com/cilium/cilium` — affected >=1.10.0 <1.10.11
- Go: `github.com/cilium/cilium` — affected >=0 <1.9.16

## Details
### Impact

If an attacker is able to perform a container escape of a container running as root on a host where Cilium is installed, the attacker can leverage Cilium's Kubernetes service account to gain access to cluster privileges that are more permissive than what is minimally required to operate Cilium. In affected releases, this service account had access to modify and delete `Pod` and `Node` resources. 

### Patches

The problem has been fixed and is available on versions >=1.9.16, >=1.10.11, >=1.11.5

### Workarounds

There are no workarounds available.

### Acknowledgements

The Cilium community has worked together with members of Isovalent, Amazon and Palo Alto Networks to prepare these mitigations.  Special thanks to Micah Hausler (AWS), Robert Clark (AWS), Yuval Avrahami (Palo Alto Networks), and Shaul Ben Hai (Palo Alto Networks) for their cooperation.

### For more information

If you have any questions or comments about this advisory:

Email us at [security@cilium.io](mailto:security@cilium.io)

## References
- https://github.com/cilium/cilium/security/advisories/GHSA-fmrf-gvjp-5j5g
- https://nvd.nist.gov/vuln/detail/CVE-2022-29179
- https://github.com/cilium/cilium/releases/tag/v1.10.11
- https://github.com/cilium/cilium/releases/tag/v1.11.5
- https://github.com/cilium/cilium/releases/tag/v1.9.16
- github.com/cilium/cilium
