# [M] source-controller leaks Azure Storage SAS token into logs

## Summary
Severity: Medium
Advisory: GHSA-v554-xwgw-hc3w
CVE: CVE-2024-31216
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-v554-xwgw-hc3w
Type: github-advisory

## Affected
- Go: `github.com/fluxcd/source-controller` — affected >=0 <1.2.5

## Details
### Impact

When source-controller is configured to use an [Azure SAS token](https://v2-2.docs.fluxcd.io/flux/components/source/buckets/#azure-blob-sas-token-example) when connecting to Azure Blob Storage, the token was logged along with the Azure URL when the controller encountered a connection error. An attacker with access to the source-controller logs could use the token to gain access to the Azure Blob Storage until the token expires.

### Patches

This vulnerability was fixed in source-controller **v1.2.5**.

### Workarounds

There is no workaround for this vulnerability except for using a different auth mechanism such as [Azure Workload Identity](https://v2-2.docs.fluxcd.io/flux/components/source/buckets/#azure). 

### Credits

This issue was reported and fixed by Jagpreet Singh Tamber (@jagpreetstamber) from the Azure Arc team.

### References

https://github.com/fluxcd/source-controller/pull/1430

### For more information

If you have any questions or comments about this advisory:

- Open an issue in the source-controller repository.
- Contact us at the CNCF Flux Channel.

## References
- https://github.com/fluxcd/source-controller/security/advisories/GHSA-v554-xwgw-hc3w
- https://nvd.nist.gov/vuln/detail/CVE-2024-31216
- https://github.com/fluxcd/source-controller/pull/1430
- https://github.com/fluxcd/source-controller/commit/915d1a072a4f37dd460ba33079dc094aa6e72fa9
- https://github.com/fluxcd/source-controller
