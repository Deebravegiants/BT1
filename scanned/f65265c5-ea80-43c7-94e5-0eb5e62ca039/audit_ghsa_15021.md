# [M] @strapi/plugin-upload  has a Denial-of-Service via Improper Exception Handling

## Summary
Severity: Medium
Advisory: GHSA-pm9q-xj9p-96pm
CVE: CVE-2024-31217
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-12
Source: https://github.com/advisories/GHSA-pm9q-xj9p-96pm
Type: github-advisory

## Affected
- npm: `@strapi/plugin-upload` — affected >=0 <4.22.0

## Details
### Summary
A Denial-of-Service was found in the media upload process causing the server to crash without restarting, affecting either development and production environments.

### Details
Usually, errors in the application cause it to log the error and keep it running for other clients. This behavior, in contrast, stops the server execution, making it unavailable for any clients until it's manually restarted. 

### PoC
Due to a bug in what we believe to be Burp’s decoding system, we couldn’t produce a valid file to easily reproduce the vulnerability. Instead, the issue can be reproduced by following these steps:
1. Configure Burp’s proxy between a browser and a Strapi server
2. Log in and upload an image through the Media Library page while having Burp’s interceptor turned on
3. After capturing the upload POST request in Burp, add `%00` at the end of the file extension from the `Content-Disposition`, in the filename parameter (See reference image 1 below)
4. Using the cursor, select the added `%00` and right-click it. Click in Convert selection > URL > URL decode to transform the selected text into a null byte
5. Forward the modified request. The server should print an error and crash with the error `ERR_INVALID_ARG_VALUE` (See reference log 1 below)

By following the data flow, we reached the [line of code](https://github.com/strapi/strapi/blob/f1dd5cc8eef574bac6679aab6f93276e57497328/packages/providers/upload-local/src/index.ts#L86) where we believe the DoS is being caused.
The simpler way of fixing this vulnerability seems to be avoiding the error thrown by whitelisting the characters used in the extension.

#### Reference Image 1
![image](https://github.com/strapi/strapi/assets/8593673/c95278a1-1727-485e-b6f8-276074d9dd42)

#### Reference Log 1
```
[2024-03-22 10:23:42.629] http: POST /upload (22 ms) 400
node:internal/fs/utils:379
  const err = new ERR_INVALID_ARG_VALUE(
              ^

TypeError [ERR_INVALID_ARG_VALUE]: The argument 'path' must be a string, Uint8Array, or URL without null bytes. Received '/mnt/storage/Development/GHSA-pm9q-xj9p-96pm/public/uploads/replaceme_png_88efe6a165.png\x00'
    at new WriteStream (node:internal/fs/streams:340:5)
    at Object.createWriteStream (node:fs:3123:10)
    at /mnt/storage/Development/GHSA-pm9q-xj9p-96pm/node_modules/@strapi/provider-upload-local/dist/index.js:71:33
    at new Promise (<anonymous>)
    at Object.uploadStream (/mnt/storage/Development/GHSA-pm9q-xj9p-96pm/node_modules/@strapi/provider-upload-local/dist/index.js:68:16)
    at Object.uploadStream (/mnt/storage/Development/GHSA-pm9q-xj9p-96pm/node_modules/@strapi/plugin-upload/server/register.js:80:35)
    at Object.upload (/mnt/storage/Development/GHSA-pm9q-xj9p-96pm/node_modules/@strapi/plugin-upload/server/services/provider.js:16:46)
    at Object.uploadImage (/mnt/storage/Development/GHSA-pm9q-xj9p-96pm/node_modules/@strapi/plugin-upload/server/services/upload.js:220:48) {
  code: 'ERR_INVALID_ARG_VALUE'
}
```

### Impact
Denial-of-Service occurs when a service becomes unavailable for users or other services.
By sending a specially-crafted request, the server crashes without restarting. The entire server crashes with the thrown error instead of crashing only the single request and returning error 500 to the user.
Any user with access to the file upload functionality is able to exploit this vulnerability, affecting applications running in both development mode and production mode as well.

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-pm9q-xj9p-96pm
- https://nvd.nist.gov/vuln/detail/CVE-2024-31217
- https://github.com/strapi/strapi/commit/a0da7e73e1496d835fe71a2febb14f70170135c7
- https://github.com/strapi/strapi
