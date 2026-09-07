# [M] Cross-site Scripting when rendering error messages in laminas-form

## Summary
Severity: Medium
Advisory: GHSA-jq4p-mq33-w375
CVE: CVE-2022-23598
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-jq4p-mq33-w375
Type: github-advisory

## Affected
- Packagist: `laminas/laminas-form` — affected >=3.1.0 <3.1.1
- Packagist: `laminas/laminas-form` — affected >=3.0.0 <3.0.2
- Packagist: `laminas/laminas-form` — affected >=0 <2.17.1

## Details
### Impact

When rendering validation error messages via the `formElementErrors()` view helper shipped with laminas-form, many messages will contain the submitted value. However, in vulnerable versions of laminas-form, the value was not being escaped for HTML contexts, which can potentially lead to a Reflected Cross-Site Scripting (XSS) attack.

### Patches

The following versions were issued to mitigate the vulnerability:

- 2.17.1
- 3.0.2
- 3.1.1

### Workarounds

At the top of a view script where you call the `formElementErrors()` view helper, place the following code:

```php
use Laminas\Form\ElementInterface;
use Laminas\View\PhpRenderer;

$escapeMessages = function (ElementInterface $formOrElement, PhpRenderer $renderer): void {
    $messages = $element->getMessages();
    if (! $messages) {
        return;
    }

    $escaped  = [];
    array_walk_recursive(
        $messages,
        static function (string $item) use (&$escaped, $renderer): void {
            $escaped[] = $renderer->escapeHtml($item);
        }
    };

    $element->setMessages($escaped);
};
```

Before calling `formElementErrors()` with a form, fieldset, or element, call the above closure as follows

```php
// Usage with a form
// $this is the view renderer
$escapeMessages($form, $this);

// Usage with a fieldset
// $this is the view renderer
$escapeMessages($fieldset, $this);

// Usage with a form element
// $this is the view renderer
$escapeMessages($element, $this);
```

### For more information

If you have any questions or comments about this advisory:

* [Open an issue](https://github.com/laminas/laminas-form/issues/new)
* Email us at [security@getlaminas.org](mailto:security@getlaminas.org)

## References
- https://github.com/laminas/laminas-form/security/advisories/GHSA-jq4p-mq33-w375
- https://nvd.nist.gov/vuln/detail/CVE-2022-23598
- https://github.com/laminas/laminas-form/commit/43005a3ec4c2292d4f825273768d9b884acbca37
- https://getlaminas.org/security/advisory/LP-2022-01
- https://github.com/laminas/laminas-form
- https://github.com/laminas/laminas-form/releases/tag/2.17.1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFF6WJ5I7PSEBRF6I753WKE2BXFBGQXE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SLNABVK26CE4PFL57VLY242FW3QY4CPC
