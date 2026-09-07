# [M] Svelecte item names vulnerable to execution of arbitrary JavaScript

## Summary
Severity: Medium
Advisory: GHSA-7h45-grc5-89wq
CVE: CVE-2023-38687
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-14
Source: https://github.com/advisories/GHSA-7h45-grc5-89wq
Type: github-advisory

## Affected
- npm: `svelecte` — affected >=0 <3.16.3

## Details
### Summary

Svelecte item names are rendered as raw HTML with no escaping. This allows the injection of arbitrary HTML into the Svelecte dropdown. This can be exploited to execute arbitrary JavaScript whenever a Svelecte dropdown is opened.

### Details

Item names given to Svelecte appear to be directly rendered as HTML by the default item renderer. This means that any HTML tags in the name are rendered as HTML elements not as text.

Note that the custom item renderer shown in https://mskocik.github.io/svelecte/#item-rendering is also vulnerable to the same exploit.

To prevent this all special HTML characters in item names should be escaped (for example using `document.createTextNode()`).

### PoC
```svelte
<script>
    import Svelecte from 'svelecte';
    
    const list = [
        { id: 1, name: `Item 1` },
        { id: 2, name: `Item 2<img style="display:none;" src=1 onerror="alert('JavaScript executed!');"/>` },
        { id: 3, name: 'Item 3'}
    ];
</script>
    
<Svelecte options={list}></Svelecte>
```

This code snippet demonstrates how the vulnerability can be used to execute arbitrary JavaScript without the user's knowledge when the Svelecte dropdown is opened (note that visually item 2 appears identical to other items).
In this case the script is hardcoded, but in practice the real danger is that some applications may use Svelecte with items that are created by users or come from low-trust sources where someone else could add a malicious script to the item name.

### Impact

Any site that uses Svelecte with dynamically created items either from an external source or from user-created content could be vulnerable to an XSS attack (execution of untrusted JavaScript), clickjacking or any other attack that can be performed with arbitrary HTML injection.
The actual impact of this vulnerability for a specific application depends on how trustworthy the sources that provide Svelecte items are and the steps that the application has taken to mitigate XSS attacks. XSS attacks using this vulnerability are mostly mitigated by a Content Security Policy that blocks inline JavaScript.

## References
- https://github.com/mskocik/svelecte/security/advisories/GHSA-7h45-grc5-89wq
- https://nvd.nist.gov/vuln/detail/CVE-2023-38687
- https://github.com/mskocik/svelecte
