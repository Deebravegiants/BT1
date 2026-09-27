# [M] Duplicate plugin entries in Helm

## Summary
Severity: Medium
Advisory: BIT-helm-2020-15187
Aliases: CVE-2020-15187, GHSA-c52f-pq47-2r9j
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-helm-2020-15187
Type: osv

## Affected
- Bitnami: `helm` — affected >=3.0.0 <3.3.2

## Details
In Helm before versions 2.16.11 and 3.3.2, a Helm plugin can contain duplicates of the same entry, with the last one always used. If a plugin is compromised, this lowers the level of access that an attacker needs to modify a plugin's install hooks, causing a local execution attack.
To perform this attack, an attacker must have write access to the git repository or plugin archive (.tgz) while being downloaded (which can occur during a MITM attack on a non-SSL connection). This issue has been patched in Helm 2.16.11 and Helm 3.3.2.
As a possible workaround make sure to install plugins using a secure connection protocol like SSL.

## References
- https://github.com/helm/helm/commit/d9ef5ce8bad512e325390c0011be1244b8380e4b
- https://github.com/helm/helm/security/advisories/GHSA-c52f-pq47-2r9j
- https://nvd.nist.gov/vuln/detail/CVE-2020-15187
- https://github.com/helm/helm/commit/6aab63765f99050b115f0aec3d6350c85e8da946
- https://github.com/helm/helm/commit/ac7c07c37d87e09797f714fb57aa5e9cb99d9450
- https://github.com/helm/helm/commit/b0296c0522e837d65f944beefa3fb64fd08ac304
- https://github.com/helm/helm/commit/c8d6b01d72c9604e43ee70d0d78fadd54c2d8499
- https://github.com/helm/helm/commit/f2ede29480b507b7d8bb152dd8b6b86248b00658
