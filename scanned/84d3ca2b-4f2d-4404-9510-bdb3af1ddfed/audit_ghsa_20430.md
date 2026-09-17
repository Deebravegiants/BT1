# [M] jsx-slack insufficient patch for CVE-2021-43838 ReDoS

## Summary
Severity: Medium
Advisory: GHSA-hp68-xhvj-x6j6
CVE: CVE-2021-43843
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-hp68-xhvj-x6j6
Type: github-advisory

## Affected
- npm: `jsx-slack` — affected >=0 <4.5.2

## Details
We found the patch for CVE-2021-43838 in jsx-slack v4.5.1 is insufficient to save from Regular Expression Denial of Service (ReDoS) attack.

This vulnerability affects to jsx-slack v4.5.1 and earlier versions.

### Impact

If attacker can put a lot of JSX elements into `<blockquote>` tag _with including multibyte characters_, an internal regular expression for escaping characters may consume an excessive amount of computing resources.

```javascript
/** @jsxImportSource jsx-slack */
import { Section } from 'jsx-slack'

console.log(
  <Section>
    <blockquote>
      {[...Array(40)].map(() => (
        <p>亜</p>
      ))}
    </blockquote>
  </Section>
)
```

v4.5.1 has released by passing the test against ASCII characters but missed the case of multibyte characters.
https://github.com/yhatt/jsx-slack/security/advisories/GHSA-55xv-f85c-248q

### Patches

jsx-slack v4.5.2 has updated regular expressions for escaping blockquote characters to prevent catastrophic backtracking. It is also including an updated test case to confirm rendering multiple tags in `<blockquote>` with multibyte characters.

### References

- https://github.com/yhatt/jsx-slack/commit/46bc88391d89d5fda4ce689e18ca080bcdd29ecc

### Credits

Thanks to @hieki for finding out this vulnerability.

## References
- https://github.com/yhatt/jsx-slack/security/advisories/GHSA-55xv-f85c-248q
- https://github.com/yhatt/jsx-slack/security/advisories/GHSA-hp68-xhvj-x6j6
- https://nvd.nist.gov/vuln/detail/CVE-2021-43843
- https://github.com/yhatt/jsx-slack/commit/46bc88391d89d5fda4ce689e18ca080bcdd29ecc
- https://github.com/yhatt/jsx-slack/releases/tag/v4.5.2
- https://github.com/yhatt/jsx-slack/security
