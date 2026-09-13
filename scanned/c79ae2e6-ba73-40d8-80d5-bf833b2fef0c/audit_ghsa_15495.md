# [M] IDOR vulnerability in account profile page

## Summary
Severity: Medium
Advisory: GHSA-rw3j-574h-mrcq
CVE: CVE-2024-39319
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-09-26
Source: https://github.com/advisories/GHSA-rw3j-574h-mrcq
Type: github-advisory

## Affected
- Packagist: `aimeos/ai-controller-frontend` — affected >=2024.04.1 <2024.04.2
- Packagist: `aimeos/ai-controller-frontend` — affected >=2023.04.1 <2023.10.9
- Packagist: `aimeos/ai-controller-frontend` — affected >=2022.04.1 <2022.10.8
- Packagist: `aimeos/ai-controller-frontend` — affected >=2021.04.1 <2021.10.8
- Packagist: `aimeos/ai-controller-frontend` — affected >=0 <2020.10.15

## Details
### Impact
Insecure direct object reference allowing an attacker to disable subscriptions and reviews of another customer

## References
- https://github.com/aimeos/ai-controller-frontend/security/advisories/GHSA-rw3j-574h-mrcq
- https://nvd.nist.gov/vuln/detail/CVE-2024-39319
- https://github.com/aimeos/ai-controller-frontend/commit/2ad5c062a629af374da470a319914c321c9bfee2
- https://github.com/aimeos/ai-controller-frontend/commit/53eebdc51fae34440dfd768a7811c169c7779aa9
- https://github.com/aimeos/ai-controller-frontend/commit/5833db6d18a889b94dc036dfb84b6f5cca73fbac
- https://github.com/aimeos/ai-controller-frontend/commit/6ea6b82f5a1fc18c574cb6f97225930d139b14a5
- https://github.com/aimeos/ai-controller-frontend/commit/700da5ea2b622724b68c8684346bf74ac3bbca9b
- https://github.com/aimeos/ai-controller-frontend/commit/7c93139f86eff9ec26b117a8918e06ce6cc0000f
- https://github.com/aimeos/ai-controller-frontend/commit/ae7baa3f2fbf594c2c1e4b1aae83364a84b241a6
- https://github.com/aimeos/ai-controller-frontend/commit/cd8c95aa4663f54bd66a69c5952f2e42405426f3
- https://github.com/aimeos/ai-controller-frontend/commit/d4eac06f3a25330c089d8be4397f2ab1936dd9bb
- https://github.com/aimeos/ai-controller-frontend/commit/f7c6a9ce2a6f5a9ad4af31313508870a78398f85
- https://github.com/aimeos/ai-controller-frontend
