# [C] YesWiki has Unsafe eval() in its Formula Calculato, Leading to Remote Code Execution & Denial of Service

## Summary
Severity: Critical
Advisory: GHSA-px5m-h76g-p7p8
CVE: CVE-2026-52778
CWE: CWE-1333, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-px5m-h76g-p7p8
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.6

## Details
### Summary

An unsafe execution vulnerability exists in the Bazar form field calculator (CalcField.php) of YesWiki. The application attempts to sanitize user-defined mathematical formulas using a complex recursive regular expression before passing them to the PHP eval() function. This implementation is inherently flawed: it is vulnerable to Regular Expression Denial of Service (ReDoS / Stack Overflow) which can crash the server, and it creates a high-risk architecture where any logic bypass directly results in arbitrary PHP code execution.

### Details

Affected Component
- **File**: tools/bazar/fields/CalcField.php
- **Method**: formatValuesBeforeSave($entry)
- **Vulnerable Mechanism:** Combination of a complex recursive regex validation followed by eval().


The code attempts to implement a sandbox for mathematical operations by verifying the formula structure before executing it:

```
$regexpToCheckIfMathFormula = '/^((' . $number . '|' . $functions . '\s*\((?1)+\)|\((?1)+\))(?:' . $operators . '(?1))?)+$/';

if (preg_match($regexpToCheckIfMathFormula, $formula)) {
    $formula = preg_replace('!pi|π!', 'pi()', $formula);
    try {
        eval("\$value = $formula;");  // VULNERABLE LINE
// ...
```
### Architectural Flaws

**PCRE Stack Overflow & ReDoS (The Immediate Exploit):**

The regex definition heavily relies on a recursive pattern (?1)+. In PHP's PCRE engine, deeply nested recursive patterns are processed on the system stack. If an attacker inputs a formula with thousands of nested parentheses or repeating groups, the engine will either trigger a pcre.recursion_limit exhaust (returning false or null) or cause a Segmentation Fault, instantly crashing the PHP process (Denial of Service).

**The "Validation-Before-Substitution" Trap:**

The regex checks the $formula variable after it has tokenized and reassembled the input string. If any underlying function called during tokenization (like testEntryValue or future updates to getEntryValue) returns or leaks an unexpected string format, the string structure changes.

**Complete Trust in eval():**

Using eval() as a math parser means the application's security perimeter relies entirely on a single regular expression. History shows that complex regex sanitizers for script evaluation are consistently bypassed via edge-case syntaxes, character encoding tricks, or PCRE engine bugs.

### PoC

**Scenario A: Remote Denial of Service (Server Crash)**

An attacker with rights to create or edit a Bazar form adds a Calc field and injects a deeply nested recursive mathematical structure.

Payload:

`((((((((((((((((((((((((((((((((((((((((((1+1))))))))))))))))))))))))))))))))))))))))))))
`

(Multiplied by 2000 to 5000 iterations depending on the server's pcre.recursion_limit and stack configuration).

The PCRE engine runs out of stack memory, leading to an immediate crash of the PHP-FPM worker or Apache process handling the request, rendering the service unavailable.

**Scenario B: Logical Bypass to RCE**

Because eval() executes raw PHP code, if an attacker successfully fuzzes the recursive pattern or exploits an unpatched vulnerability in the specific PCRE library version installed on the host OS, they can slip a PHP payload through the validation block.
 
Payload:

`abs(1) + system('id')
`

If a validation bypass occurs, the string evaluates as native PHP, granting the attacker the privileges of the www-data (web server) user, leading to a full host compromise.

### Impact

- Confidentiality: HIGH. Attackers can read sensitive system files (e.g., /etc/passwd, .env configuration files).

- Integrity: HIGH. Attackers can modify application files, inject backdoors, or alter the database content.

- Availability: HIGH. Attackers can easily bring down the web service via the ReDoS/Segmentation Fault vector.

### Remediation & Mitigation

- Do not use regular expressions to safe-guard eval(). Instead, replace the execution block with a dedicated, safe Abstract Syntax Tree (AST) math parser or an expression language component that cannot execute system context.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-px5m-h76g-p7p8
- https://nvd.nist.gov/vuln/detail/CVE-2026-52778
- https://github.com/YesWiki/yeswiki/commit/dd2bd8fb099de0d21504bda8a810693b3fcb8e52
- https://github.com/YesWiki/yeswiki
- https://github.com/YesWiki/yeswiki/releases/tag/v4.6.6
