# [H] Frigte has broken access control viewer user can delete admin and other users account

## Summary
Severity: High
Advisory: GHSA-vg28-83rp-8xx4
CVE: CVE-2026-33125
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-vg28-83rp-8xx4
Type: github-advisory

## Affected
- PyPI: `frigate` — affected >=0

## Details
### Summary
Users with the viewer role can delete admin and other users account. It this leads to denial of service and affects data integrity.

### Details
Endpoint `DELETE /api/users/admin` is enable to anonymous user.

<img width="436" height="100" alt="obraz" src="https://github.com/user-attachments/assets/817f9c47-7bd9-4247-a2f1-0f40778ab229" />

### PoC
I deleted admin user on `demo.frigate.video`:

<img width="1091" height="222" alt="obraz" src="https://github.com/user-attachments/assets/34f50a13-3bb7-4aa8-99fa-bd815b3dc915" />


### Impact
It this leads to denial of service and affects data integrity.

### Recommended Fixes
Restrict access to the endpoint to authenticated admin users only:
Add `dependencies=[Depends(require_role(["admin"]))])` to this endpoint.

## References
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-vg28-83rp-8xx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33125
- https://github.com/blakeblackshear/frigate
- https://github.com/blakeblackshear/frigate/releases/tag/v0.16.3
