# [C] Directus allows unauthenticated file upload and file modification due to lacking input sanitization

## Summary
Severity: Critical
Advisory: GHSA-mv33-9f6j-pfmc
CVE: CVE-2025-55746
CWE: CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-mv33-9f6j-pfmc
Type: github-advisory

## Affected
- npm: `directus` — affected >=10.8.0 <11.9.3
- npm: `@directus/api` — affected >=14.1.0 <28.0.2

## Details
## Summary

A vulnerability exists in the file update mechanism which allows an unauthenticated actor to modify existing files with arbitrary contents (without changes being applied to the files' database-resident metadata) and / or upload new files, with arbitrary content and extensions, which won't show up in the Directus UI.

## Details

Directus exposes the CRUD operations for uploading or handling files under the `/files` route.

The endpoint handler is responsible for updating an existing file identified by the provided primary key specified through the `pk` parameter. Primary keys are UUID values such as `/files/927b3abf-fb4b-4c66-bdaa-eb7dc48a51cb`. Here the `filename_disk` value is never sanitized, it's possible to pass a path containing traversal sequences (`../`) through it, but a fully arbitrary file write is not possible in case the "local" storage handler is used. (Other storage implementations haven't been checked during the research process). The `packages/storage-driver-local/src/index.ts` file defines two relevant functions: `write` and `fullpath`.

The `write` method uses the `fullPath` method to create the absolute path for the to-be-created file. The `join` method is used to create the final path string. As the `fullPath` method uses `join` to create a relative path starting with the separator to be added under the download dir, this call normalizes the path and further upwards traversal is not possible during the write operation. With that being said, it is still possible, to make the system "ignore" the `temp_` prefix given to the file, resulting in an arbitrarily named file being placed in the upload folder.

As a summary for the vulnerability:

- It is possible, to change the contents of an existing file, as an existing UUID can be specified as the file name
        - The metadata won't change, so the mime type cannot be modified
        - This also makes the changes happen "silently", without directus knowing about the changes
- A new, previously non-existent file can be created with arbitrary contents
        - The file won't show up in on the Directus UI, it can only be seen through other means (such as shell access)
- An extension MUST be defined for the file to be modified
        - This prevents us from uploading executables or malware with no extensions, but these wouldn't be executable either way

Recommendations for fixing the vulnerability can be found in later chapters.

## Requirements 

As providing a primary key is required for successful exploitation, at least one asset with a known UUID must be available for an attacker. This can usually be achieved by browsing an application that uses the given Directus instance to provide images. 

Naturally, the instance needs to be accessible over the network used by the attacker as well.

Once network access and knowledge of at least one file UUID is available for the attacker, exploitation can be done by sending a single request.

## Potential impacts

The impact of successful exploitation is highly dependent on how Directus is set up to be used by a different application. Many different configurations can be created, but the following are likely the most noteworthy:

1. Setting up a phishing site

SVGs can be used to set up very sophisticated looking pages, as it allows the embedding of HTML, CSS and scripts. The issue is once again with the `default-src: none` CSP settings. This setting prevents the use of CSS in the SVG file, so the created page will look strange.

While the page obviously looks strange, it's important to notice that since the domain checks out, the browser could fill out the login forms, making for a much more convincing page as shown below:

An error message can be used to make it look like an error in the system!

2. Server serves files directly from the upload directory:

In this setup, a server such ash nginx serves files in a static manner. The served files are loaded from a "public" folder made accessible through Directus as it's recommended in the files API docs. Quoting: "make a public folder and allow access to this", except the upload folder is directly served by the server:

Since the files loaded by the server are sourced directly from the file storage, the arbitrary file write might allow an attacker to upload a webshell into the folder, giving it an arbitrary file extension. As the extension checks out as a valid PHP file for instance, and the contents are correct code, an attacker can achieve unauthenticated code execution on the server.

3. Poisoning hosted files

The previous examples focused on active exploitation, but it's important to mention that the vulnerability allows for arbitrary changes in files. This can be used for many different attack primitives. Let's consider the following scenario: Directus is used not only to serve contents on a company's web page, but internally as well. Onboarding documents for new entries are hosted on the instance. Manuals with links to internal services are provided through PDF files. If the file can be accessed and modified by an attacker, it would be trivial to set up a spoofed instance which receives credentials for internal services but redirects to the original, internal service right after. 

## Credits

The bug was discovered by Zombor Máté, a security researcher at PCA Cyber Security (https://pcacybersecurity.com/)

## References
- https://github.com/directus/directus/security/advisories/GHSA-mv33-9f6j-pfmc
- https://nvd.nist.gov/vuln/detail/CVE-2025-55746
- https://github.com/directus/directus/commit/d84dcc36f75fc5c858d43746b8f9c426c38d696b
- https://github.com/directus/directus
