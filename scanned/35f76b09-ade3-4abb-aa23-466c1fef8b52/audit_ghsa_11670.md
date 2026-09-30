# [M] Roadiz has Server-Side Request Forgery (SSRF) in roadiz/documents

## Summary
Severity: Medium
Advisory: GHSA-rc55-58f4-687g
CVE: CVE-2026-33486
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-rc55-58f4-687g
Type: github-advisory

## Affected
- Packagist: `roadiz/documents` — affected >=2.7.0 <2.7.9
- Packagist: `roadiz/documents` — affected >=2.6.0 <2.6.28
- Packagist: `roadiz/documents` — affected >=2.4.0 <2.5.44
- Packagist: `roadiz/documents` — affected >=0 <2.3.42

## Details
This vulnerability allows an authenticated attacker to read any file on the server's local file system that the web server process has access to, including highly sensitive environment variables, database credentials, and internal configuration files.

| Field | Details |
| :--- | :--- |
| **Vulnerability Class** | Server-Side Request Forgery (SSRF) & Local File Inclusion (LFI) |
| **Affected Component** | `RZ\Roadiz\Documents\DownloadedFile::fromUrl()` |
| **Prerequisites** | Authenticated user with `ROLE_ACCESS_DOCUMENTS` |

## Technical Description

The Roadiz backend features tools for importing external media, such as compiling cover art from Podcast RSS Feeds or OEmbed providers. This feature is handled by various `MediaFinders`, which ultimately pass the extracted media URLs to the `DownloadedFile::fromUrl(string $url)` parsing mechanism.

Inside `fromUrl()`, the application uses PHP's native `fopen()` function to fetch the remote resource and copy it into the local temporary directory before injecting it into the Flysystem Documents storage.

##  The Flaw

The `$url` parameter is passed to `fopen` *without any schema validation or sanitization*. In PHP, when stream wrappers are enabled, functions like `fopen` do not restrict operations to HTTP streams. If a `file://` scheme is supplied, PHP seamlessly converts the operation into a local file system read. Because an attacker tightly controls the XML feed (e.g., from a Podcast integration), they can inject a `file://` URI, forcing the CMS to "download" internal system files directly into the publicly accessible Media Library.

---

## Proof of Concept (PoC)

To reliably reproduce this vulnerability without requiring a live external URL, the attacker simply mimics the behavior of the Podcast importer manipulating the internal system.

### Step 1: Craft the Malicious Payload
The attacker creates a standard Podcast RSS XML feed (`podcast.xml`) and hosts it externally (or on an internal network reachable by the CMS). Inside this XML, the `href` attribute for the podcast thumbnail is weaponized to target a sensitive system file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Roadiz LFI Exploit</title>
    <!-- Payload triggers the local filesystem fetch via PHP streams -->
    <itunes:image href="file:///app/.env" /> 
  </channel>
</rss>
```

### Step 2: Exploit the CMS
1. Authenticate to the Roadiz Backoffice.
2. Navigate to **Documents (Media Manager)**.
3. Select **Add a document** -> **Import from URL** (or trigger a Podcast sync).
4. Supply the URL of the malicious `podcast.xml` file.

### Step 3: Extract the Data
1. The `AbstractPodcastFinder` processes the XML and feeds `file:///app/.env` directly into `DownloadedFile::fromUrl()`.
2. The Roadiz application silently reads its own `.env` file, creating a new "Document" arrayed with the contents of the file.
3. The file manifests in the Media Manager grid as a broken image icon.
4. The attacker actively downloads the newly generated Document from the dashboard, successfully extracting the framework's internal API keys, database credentials, and `APP_SECRET`.

---

## Impact Analysis

Exploitation of this vulnerability results in a total loss of **Confidentiality** for the web application and underlying operating system. 

- **Application Compromise:** An attacker can retrieve `.env`, `security.yaml`, or database `.sqlite` files, leading to complete horizontal and vertical privilege escalation.
- **System Enumeration:** The attacker can read `/etc/passwd`, enumerating system users in preparation for lateral movement.
- **Cloud Environment Compromise:** If deployed within AWS, Azure, or GCP, the SSRF vector can be pivoted to read internal cloud metadata endpoints (e.g., `http://169.254.169.254/latest/meta-data/`), allowing the attacker to steal Root IAM roles globally compromising the victim's infrastructure.

## References
- https://github.com/roadiz/core-bundle-dev-app/security/advisories/GHSA-rc55-58f4-687g
- https://nvd.nist.gov/vuln/detail/CVE-2026-33486
- https://github.com/roadiz/core-bundle-dev-app/commit/7904f690a51b88b1c72c02149ebdf85fa81f19f2
- https://github.com/roadiz/core-bundle-dev-app
