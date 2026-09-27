# [H] Authenticated arbitrary file deletion in YesWiki

## Summary
Severity: High
Advisory: GHSA-43c9-gw4x-pcx6
CVE: CVE-2025-24019
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-43c9-gw4x-pcx6
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.5.0

## Details
# Authenticated arbitrary file deletion in YesWiki <= 4.4.5

### Summary
It is possible for any authenticated user, through the use of the filemanager to delete any file owned by the user running the FastCGI Process Manager (FPM) on the host without any limitation on the filesystem's scope.

This Proof of Concept has been performed using the followings:
- YesWiki v4.4.5 (`doryphore-dev` branch, latest)
- Docker environnment (`docker/docker-compose.yml`)
- Docker v27.5.0
- Default installation

### Details
The vulnerability makes use of the `filemanager` that allows a user to manage files that are attached to a resource when they have owner permission on it. This part of the code is managed in `tools/attach/libs/attach.lib.php`

```php
public function doFileManager($isAction = false)
{
    $do = (isset($_GET['do']) && $_GET['do']) ? $_GET['do'] : '';
    switch ($do) {
        case 'restore':
            $this->fmRestore();
            $this->fmShow(true, $isAction);
            break;
        case 'erase':
            $this->fmErase();
            $this->fmShow(true, $isAction);
            break;
        case 'del':
            $this->fmDelete();
            $this->fmShow(false, $isAction);
            break;
        case 'trash':
            $this->fmShow(true, $isAction);
            break;
        case 'emptytrash':
            $this->fmEmptyTrash(); //pas de break car apres un emptytrash => retour au gestionnaire
            // no break
        default:
            $this->fmShow(false, $isAction);
    }
}
```

The **[fmErase()](https://github.com/YesWiki/yeswiki/blob/doryphore-dev/tools/attach/libs/attach.lib.php#L999)** function doesn't sanitize or verify the path that has been provided by the user in any way. Thus allowing a malicious user to specify any arbitrary file on the filesystem and having it deleted through the use of `unlink()` (as long as the user that runs the process has permission to delete it).

```php
public function fmErase()
{
    $path = $this->GetUploadPath();
    $filename = $path . '/' . ($_GET['file'] ? $_GET['file'] : '');
    if (file_exists($filename)) {
        unlink($filename);
    }
}
```

In addition to this deletion accross all the filesystem through `fmErase()`, it is also possible to delete any file attached to an existing wiki page, for instance, if user A creates a page and attaches images/documents to it, they always get uploaded to the files/ directory. If user B (malicious), knows the path of the files he can also arbitrarly delete them. (**[fmDelete()](https://github.com/YesWiki/yeswiki/blob/doryphore-dev/tools/attach/libs/attach.lib.php#L1011)** is also impacted by this case)

### PoC
#### 1. Environnement setup
> The following actions have been performed as a privileged user

First, let's create one user (in addition to the WikiAdmin user):

![poc1](https://github.com/user-attachments/assets/f977106e-0618-4594-a673-14840ed6cb83)

Restrict the edition of 'PagePrincipale' wiki page to administrators only:

![poc2](https://github.com/user-attachments/assets/c40c43dd-1b4f-48fc-b425-9d7915c626bc)

#### 2. Upload of a file on a resource not owned by our user
> The following actions have been performed as a privileged user

Second, let's upload a media to this `PagePrincipale` wiki page:

![poc3](https://github.com/user-attachments/assets/da1cf714-34d6-4d06-8768-f6e0984172fe)
![poc4](https://github.com/user-attachments/assets/3391986d-8d65-4ed0-b614-b71e9938846e)

Then view it in the page's filemanager:

![poc5](https://github.com/user-attachments/assets/821bb42c-9cb7-4209-82ac-a5884cc57eb4)

We can confirm that our file has been uploaded to the `files/` directory by directly looking at the `yeswiki` container:

![poc5 1](https://github.com/user-attachments/assets/629c88c5-744a-4203-b017-03abded00ca5)

#### 3. Arbitrary deletion (in files/)
> The following actions have been performed using an unprivileged user

Now, get the full path/name of the media in the files directory by opening it in a new tab:

![poc6](https://github.com/user-attachments/assets/43cdc5f6-5e05-4797-91d8-3bed0142d72a)

Afterwards, we need an instance of filemanager to be accessible to our user so we need to create a page that we own, here is used the agenda and the creation of a new event:

![poc7](https://github.com/user-attachments/assets/1ef17353-04d0-42c8-8a80-dc9f10ca7f80)

Call the `erase` method on the PagePrincipale's uploaded media:

![poc](https://github.com/user-attachments/assets/9d05fe78-a8ec-4835-b480-297d0f8fc037)

The media is now deleted from PagePrincipale (the button is shown when the attached media doesn't exist, it's an intended behaviour):

![poc9](https://github.com/user-attachments/assets/5d20ae80-0eaa-48c1-8411-fd1c5632f524)

It has also disappeared from the `files/` directory:

![poc10](https://github.com/user-attachments/assets/a6b3e305-ec4f-4ffb-b5df-34bfddf198b3)

This behaviour can be applied to **any** file under the `files/` directory.

#### 4. Arbitrary deletion (in /tmp/)
> The following actions have been performed using a privileged access

Finally, using the same user as the process running the app, we create a file under the `/tmp` directory:

![poc11](https://github.com/user-attachments/assets/45befa45-1023-4aed-b55a-f49864eb2174)

> The following actions have been performed using an unprivileged user

We can once again call the `erase` method using a relative path:

![poc3](https://github.com/user-attachments/assets/b9ee7d19-5f2c-4de3-9a8d-5049c2480d3e)

The file isn't here anymore:

![poc13](https://github.com/user-attachments/assets/1ec440b6-cc95-40b5-b061-22fc46b8ae67)

### Impact
This vulnerability allows any authenticated user to arbitrarly remove content from the Wiki resulting in partial loss of data and defacement/deteroriation of the website. In the context of a container installation of YesWiki without any modification, the 'yeswiki' files (for example .php) are not owned by the same user (root) as the one running the FPM process (www-data). However in a standard installation, www-data may also be the owner of the PHP files, allowing a malicious user to completely cut the access to the wiki by deleting all important PHP files (like index.php or core files of YesWiki).

### Suggestion of possible corrective measures

- Restrict the possible paths of `fmErase()` to the `upload_path` directory.

- Restrict the use of `fmErase()` to trashed files only.

```php
public function fmErase()
{
    $path = $this->GetUploadPath();
    $filename = $this->GetUploadPath() . '/' . basename(realpath(($_GET['file'] ? $_GET['file'] : ''))); //Sanitize file path
    if (file_exists($filename) && preg_match('/trash\d{14}$/', $filename)) { //Make sure that the filename ends with trash and a date
        unlink($filename);
    }
}
```

- Make sure that any request to `fmErase()` or `fmDelete()` originates from the owner of the resource to which the attachment is linked (asks a bit more than a few lines of code).

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-43c9-gw4x-pcx6
- https://nvd.nist.gov/vuln/detail/CVE-2025-24019
- https://github.com/YesWiki/yeswiki/commit/3ddd833d22703caf9025659eb174f7765df7147c
- https://github.com/YesWiki/yeswiki
