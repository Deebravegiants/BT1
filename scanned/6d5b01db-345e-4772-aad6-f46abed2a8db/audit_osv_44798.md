# [M] MISP Missing Authorization in Cryptographic Key View Exposes Signing Keys from Protected Events

## Summary
Severity: Medium
Advisory: CVE-2026-86408
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86408
Type: osv

## Details
Affected versions of MISP do not enforce parent-event visibility when serving cryptographic keys through CryptographicKeysController::view().


The vulnerable handler queried CryptographicKey directly using the supplied key ID and selected sensitive fields such as:



  *  
type


  *  
key_data


  *  
fingerprint





but did not fetch or authorize the associated parent event first.


The upstream commit explicitly states that cryptographicKeys/view could return a protected event’s signing key to any authenticated user.


The fix adds parent_id and parent_type to the lookup and then enforces authorization through the associated event using fetchSimpleEvent($user, parent_id). If the parent is not an Event, access is limited to site administrators.

Version affected: ≤2.5.45

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86408.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86408
- https://github.com/MISP/MISP/commit/2edde619b
- https://github.com/MISP/MISP
