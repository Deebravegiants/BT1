# [M] Synapse V2 state resolution weakness allows Denial of Service (DoS)

## Summary
Severity: Medium
Advisory: GHSA-3h7q-rfh9-xm4v
CVE: CVE-2024-31208
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-3h7q-rfh9-xm4v
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.105.1

## Details
### Impact

A remote Matrix user with malicious intent, sharing a room with Synapse instances before 1.105.1, can dispatch specially crafted events to exploit a weakness in how the auth chain cover index is calculated. This can induce high CPU consumption and accumulate excessive data in the database of such instances, resulting in a denial of service.

Servers in private federations, or those that do not federate, are not affected.

### Patches

Server administrators should upgrade to 1.105.1 or later.

### Workarounds

One can:
- ban the malicious users or ACL block servers from the rooms; and/or
- leave the room and purge the room using the admin API

### For more information

If you have any questions or comments about this advisory, please email us at [security AT element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-3h7q-rfh9-xm4v
- https://nvd.nist.gov/vuln/detail/CVE-2024-31208
- https://github.com/element-hq/synapse/commit/55b0aa847a61774b6a3acdc4b177a20dc019f01a
- https://github.com/element-hq/synapse
- https://github.com/element-hq/synapse/releases/tag/v1.105.1
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2024-50.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R6FCCO4ODTZ3FDS7TMW76PKOSEL2TQVB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RR53FNHV446CB37TP45GZ6F6HZLZCK3K
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VSF4NJJSTSQRJQ47PLYYSCFYKJBP7DET
