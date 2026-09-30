# [M] aimeos/ai-controller-frontend doesn't reset payment status in basket

## Summary
Severity: Medium
Advisory: CVE-2024-39325
Aliases: GHSA-m9gv-6p22-qgmj
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-07-02
Source: https://osv.dev/vulnerability/CVE-2024-39325
Type: osv

## Details
aimeos/ai-controller-frontend is the  Aimeos frontend controller. Prior to versions 2024.04.2, 2023.10.9, 2022.10.8, 2021.10.8, and 2020.10.15, aimeos/ai-controller-frontend doesn't reset the payment status of a user's basket after the user completes a purchase. Versions 2024.04.2, 2023.10.9, 2022.10.8, 2021.10.8, and 2020.10.15 fix this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39325.json
- https://github.com/aimeos/ai-controller-frontend/security/advisories/GHSA-m9gv-6p22-qgmj
- https://nvd.nist.gov/vuln/detail/CVE-2024-39325
- https://github.com/aimeos/ai-controller-frontend/commit/16b8837d2466e3665b3c826ce87934b01a847268
- https://github.com/aimeos/ai-controller-frontend/commit/24a57001e56759d1582d2a0080fc1ca3ba328630
- https://github.com/aimeos/ai-controller-frontend/commit/28549808e0f6432a34cd3fb95556deeb86ca276d
- https://github.com/aimeos/ai-controller-frontend/commit/b1960c0b6e5ee93111a5360c9ce949b3e7528cf7
- https://github.com/aimeos/ai-controller-frontend/commit/dafa072783bb692f111ed092d9d2932c113eb855
