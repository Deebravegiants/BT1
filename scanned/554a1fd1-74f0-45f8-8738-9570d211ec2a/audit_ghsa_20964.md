# [H] Indy's NODE_UPGRADE transaction vulnerable to remote code execution

## Summary
Severity: High
Advisory: GHSA-r6v9-p59m-gj2p
CVE: CVE-2022-31020
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-02
Source: https://github.com/advisories/GHSA-r6v9-p59m-gj2p
Type: github-advisory

## Affected
- PyPI: `indy-node` — affected >=0 <1.12.5rc1

## Details
### Impact

The `pool-upgrade` request handler in Indy-Node `<=1.12.4` allows an improperly authenticated attacker to remotely execute code on nodes within the network.

Network operators are strongly encouraged to upgrade to the latest Indy-Node release `>=1.12.5` as soon as possible.

### Patches

The `pool-upgrade` request handler in Indy-Node `>=1.12.5` has been updated to properly authenticate `pool-upgrade` transactions before any processing is performed by the request handler.  The transactions are further sanitized to prevent remote code execution.

### Mitigations

Network operators are strongly encouraged to upgrade to the latest Indy-Node release `>=1.12.5` as soon as possible.

### Acknowledgements
Thank you to @shakreiner at CyberArk Labs for finding and responsibly disclosing this issue.

## References
- https://github.com/hyperledger/indy-node/security/advisories/GHSA-r6v9-p59m-gj2p
- https://nvd.nist.gov/vuln/detail/CVE-2022-31020
- https://github.com/hyperledger/indy-node/commit/fe507474f77084faef4539101e2bbb4d508a97f5
- https://github.com/hyperledger/indy-node
- https://github.com/hyperledger/indy-node/releases/tag/v1.12.5
- https://github.com/pypa/advisory-database/tree/main/vulns/indy-node/PYSEC-2022-265.yaml
