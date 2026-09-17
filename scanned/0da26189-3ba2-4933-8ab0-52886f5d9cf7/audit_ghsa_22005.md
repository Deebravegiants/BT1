# [H] Use of Hard-coded Cryptographic Key in Netmaker

## Summary
Severity: High
Advisory: GHSA-86f3-hf24-76q4
CVE: CVE-2022-23650
CWE: CWE-321, CWE-798
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-22
Source: https://github.com/advisories/GHSA-86f3-hf24-76q4
Type: github-advisory

## Affected
- Go: `github.com/gravitl/netmaker` — affected >=0 <0.8.5
- Go: `github.com/gravitl/netmaker` — affected >=0.9.0 <0.9.4

## Details
### Impact
There is a hard-coded cryptographic key in the code base which can be exploited to run admin commands on a remote server, if you know the address and username of the admin. This effects the server (netmaker) component, and not clients.

### Patches
This has been patched in Netmaker v0.8.5, v0.9.4, and v0.10.0. If you are running these versions, the fix is to perform the following:

1. docker-compose down
2. docker pull gravitl/netmaker:( version )
3. docker-compose up -d

#### Additional Information
If you are running **any other version**, you will need to upgrade to one of these three versions. If you have a special circumstance that requires running a different version, let us know and we may be able to build a custom patch.

### For more information
If you have any questions or comments about this advisory:
* Email us at [info@gravitl.com](mailto:info@gravitl.com)

## References
- https://github.com/gravitl/netmaker/security/advisories/GHSA-86f3-hf24-76q4
- https://nvd.nist.gov/vuln/detail/CVE-2022-23650
- https://github.com/gravitl/netmaker/pull/781/commits/1bec97c662670dfdab804343fc42ae4b1d050a87
- https://github.com/gravitl/netmaker/commit/3d4f44ecfe8be4ca38920556ba3b90502ffb4fee
- https://github.com/gravitl/netmaker/commit/e9bce264719f88c30e252ecc754d08f422f4c080
- https://github.com/gravitl/netmaker
