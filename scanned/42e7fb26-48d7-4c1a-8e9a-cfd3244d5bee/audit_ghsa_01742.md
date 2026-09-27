# [C] Negative charge in shopping cart in Shopizer

## Summary
Severity: Critical
Advisory: GHSA-w8rc-pgxq-x2cj
CVE: CVE-2020-11007
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-04-22
Source: https://github.com/advisories/GHSA-w8rc-pgxq-x2cj
Type: github-advisory

## Affected
- Maven: `com.shopizer:sm-core-model` — affected >=0 <2.11.0

## Details
### Impact
Using API or Controller based versions negative quantity is not adequately validated hence creating incorrect shopping cart and order total. 

### Patches
Adding a back-end verification to check that quantity parameter isn't negative. If so, it is set to 1. Patched in 2.11.0

### Workarounds
Without uprading, it's possible to just apply the fixes in the same files it's done for the patch. Or you use javax constraint validation on the quantity parameter.

### References
[Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
[Using bean validation constraint](https://javaee.github.io/tutorial/bean-validation002.html)
[Commits with fixes](https://github.com/shopizer-ecommerce/shopizer/commit/929ca0839a80c6f4dad087e0259089908787ad2a)
CVE Details below : 
[Mitre](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-11007)
[NVD](https://nvd.nist.gov/vuln/detail/CVE-2020-11007)

### Credits
Found and solved by Yannick Gosset from Aix-Marseille University cybersecurity
master program supervised by Yassine Ilmi

## References
- https://github.com/shopizer-ecommerce/shopizer/security/advisories/GHSA-w8rc-pgxq-x2cj
- https://nvd.nist.gov/vuln/detail/CVE-2020-11007
- https://github.com/shopizer-ecommerce/shopizer/commit/929ca0839a80c6f4dad087e0259089908787ad2a
