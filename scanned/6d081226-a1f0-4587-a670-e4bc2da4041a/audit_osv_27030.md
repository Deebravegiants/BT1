# [C] Privileged User using traversal to read system files

## Summary
Severity: Critical
Advisory: CVE-2024-0550
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-0550
Type: osv

## Details
A user who is privileged already `manager` or `admin` can set their profile picture via the frontend API using a relative filepath to then user the PFP GET API to download any valid files.

The attacker would have to have been granted privileged permissions to the system before executing this attack.

## References
- https://huntr.com/bounties/c6afeb5e-f211-4b3d-aa4b-6bad734217a6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0550.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0550
- https://github.com/mintplex-labs/anything-llm/commit/e1dcd5ded010b03abd6aa32d1bf0668a48e38e17
