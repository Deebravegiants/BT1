# [M] Magento LTS vulnerable to stored XSS in admin file form

## Summary
Severity: Medium
Advisory: GHSA-gp6m-fq6h-cjcx
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-02-27
Source: https://github.com/advisories/GHSA-gp6m-fq6h-cjcx
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.5.0
- Packagist: `openmage/magento-lts` — affected >=0 <19.5.3

## Details
### Summary
OpenMage is affected by a stored Cross-Site Scripting (XSS) vulnerability that could be abused by a low-privileged attacker to inject malicious scripts into vulnerable form fields.

### Details
`Mage_Adminhtml_Block_System_Config_Form_Field_File` does not escape filename value in certain situations.
Same as: https://nvd.nist.gov/vuln/detail/CVE-2024-20717

### PoC
1. Create empty file with this filename: `<img src=x onerror=alert(1)>.crt`
2. Go to _System_ > _Configuration_ > _Sales | Payment Methonds_.
3. Click **Configure** on _PayPal Express Checkout_.
4. Choose **API Certificate** from dropdown _API Authentication Methods_.
5. Choose the XSS-file and click **Save Config**.
6. Profit, alerts "1" -> XSS.
7. Reload, alerts "1" -> Stored XSS.

### Impact
Affects admins that have access to any fileupload field in admin in core or custom implementations.
Malicious JavaScript may be executed in a victim’s browser when they browse to the page containing the vulnerable field.

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-gp6m-fq6h-cjcx
- https://nvd.nist.gov/vuln/detail/CVE-2024-20717
- https://github.com/OpenMage/magento-lts
