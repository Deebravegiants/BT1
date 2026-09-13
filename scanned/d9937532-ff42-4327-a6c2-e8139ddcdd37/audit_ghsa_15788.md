# [M] @jmondi/url-to-png contains a Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vvmv-wrvp-9gjr
CVE: CVE-2024-39918
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-vvmv-wrvp-9gjr
Type: github-advisory

## Affected
- npm: `@jmondi/url-to-png` — affected >=0 <2.1.2

## Details
### Summary
When trying to add a `BLOCK_LIST` feature when the maintainer noticed they didn't sanitize the `ImageId` in the code, which leads to path traversal vulnerability. Now, this is different from a traditional path traversal issue, because as of NOW you can store the image in any place arbitrarily, and given enough time they might be able to come up with a working exploit BUT for the time being they am reporting this.  

### Details

@jmondi/url-to-png does not sanitizing the `ImageID` as in not removing special chars from the params [(extract_query_params.ts#l75)](https://github.com/jasonraimondi/url-to-png/blob/e43098e0af3a380ebc044e7f303a83933b94b434/src/middlewares/extract_query_params.ts#L75)

```js
const imageId = dateString + "." + slugify(validData.url) +configToString(params);
```

This when fed to other parts of the code such as ([filesystem.ts#L34](https://github.com/jasonraimondi/url-to-png/blob/8afc00247c1d7e6c7b37356a5f6282b486e596fa/src/lib/storage/filesystem.ts#L34))

```js
return path.join(this.storagePath, imageId) + ".png";
```

Would result in path traversal issue. 

### PoC

```
# Configuration for filesystem storage provider (optional)
STORAGE_PROVIDER=filesystem
IMAGE_STORAGE_PATH=poc
```

Set this in your `.env` file and use this as your payload. 

```
http://localhost:3089/?url=http://example.com&width=400&isDarkMode=../../../../../../../../../../../../tmp/hack
```

This will create a `.png` file in the `/tmp` section of the system.

Loom POC: https://www.loom.com/share/bd7b306cdae7445c97e68f0626e743a6 



This is valid for pretty much all the arguments (except for numeric values)

A simple fix would be to use the `slugify` for the params as well like so ([#L75](https://github.com/jasonraimondi/url-to-png/blob/e43098e0af3a380ebc044e7f303a83933b94b434/src/middlewares/extract_query_params.ts#L75))

```diff
- const imageId = dateString + "." + slugify(validData.url) + configToString(params);
+ const imageId = dateString + "." + slugify(validData.url) + slugify(configToString(params));
```


### Impact
This would be path traversal vulnerability which allows arbitrary write as of now.

## References
- https://github.com/jasonraimondi/url-to-png/security/advisories/GHSA-vvmv-wrvp-9gjr
- https://nvd.nist.gov/vuln/detail/CVE-2024-39918
- https://github.com/jasonraimondi/url-to-png/commit/e4eaeca6493b21cd515b582fd6c0af09ede54507
- https://github.com/jasonraimondi/url-to-png
- https://github.com/jasonraimondi/url-to-png/blob/e43098e0af3a380ebc044e7f303a83933b94b434/src/middlewares/extract_query_params.ts#L75
- https://github.com/jasonraimondi/url-to-png/releases/tag/v2.1.2
