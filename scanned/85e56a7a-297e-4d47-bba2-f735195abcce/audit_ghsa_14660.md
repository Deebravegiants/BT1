# [M] Python package "zhmcclient" stores passwords in clear text in its HMC and API logs

## Summary
Severity: Medium
Advisory: GHSA-p57h-3cmc-xpjq
CVE: CVE-2024-53865
CWE: CWE-312
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-p57h-3cmc-xpjq
Type: github-advisory

## Affected
- PyPI: `zhmcclient` — affected >=0 <1.18.1

## Details
### Impact

The Python package "zhmcclient" writes password-like properties in clear text into its HMC and API logs in the following cases:

* The 'boot-ftp-password' and 'ssc-master-pw' properties when creating or updating a partition in DPM mode, in the zhmcclient API and HMC logs
* The 'ssc-master-pw' and 'zaware-master-pw' properties when updating an LPAR in classic mode, in the zhmcclient API and HMC logs
* The 'ssc-master-pw' and 'zaware-master-pw' properties when creating or updating an image activation profile in classic mode, in the zhmcclient API and HMC logs
* The 'password' property when creating or updating an HMC user, in the zhmcclient API log
* The 'bind-password' property when creating or updating an LDAP server definition, in the zhmcclient API and HMC logs

This issue affects only users of the zhmcclient package that have enabled the Python loggers named "zhmcclient.api" (for the API log) or "zhmcclient.hmc" (for the HMC log) and that use the functions listed above.

### Patches

Has been fixed in zhmcclient version 1.18.1

### Workarounds

Not applicable, since fix is available.

### References

None

## References
- https://github.com/zhmcclient/python-zhmcclient/security/advisories/GHSA-p57h-3cmc-xpjq
- https://nvd.nist.gov/vuln/detail/CVE-2024-53865
- https://github.com/zhmcclient/python-zhmcclient/commit/ad32781e782d0f604c6da4680fce48e4cc1f4433
- https://github.com/zhmcclient/python-zhmcclient
