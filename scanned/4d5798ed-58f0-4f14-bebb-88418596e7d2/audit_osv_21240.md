# [C] CVE-2021-41264

## Summary
Severity: Critical
Advisory: CVE-2021-41264
Aliases: GHSA-5vp3-v4hc-gx76
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-12
Source: https://osv.dev/vulnerability/CVE-2021-41264
Type: osv

## Details
OpenZeppelin Contracts is a library for smart contract development. In affected versions upgradeable contracts using `UUPSUpgradeable` may be vulnerable to an attack affecting uninitialized implementation contracts. A fix is included in version 4.3.2 of `@openzeppelin/contracts` and `@openzeppelin/contracts-upgradeable`. For users unable to upgrade; initialize implementation contracts using `UUPSUpgradeable` by invoking the initializer function (usually called `initialize`). An example is provided [in the forum](https://forum.openzeppelin.com/t/security-advisory-initialize-uups-implementation-contracts/15301).

## References
- https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-5vp3-v4hc-gx76
- https://forum.openzeppelin.com/t/security-advisory-initialize-uups-implementation-contracts/15301
- https://github.com/OpenZeppelin/openzeppelin-contracts/commit/024cc50df478d2e8f78539819749e94d6df60592
