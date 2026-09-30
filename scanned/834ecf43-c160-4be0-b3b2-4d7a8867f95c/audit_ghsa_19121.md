# [H] Spotipy's cache file, containing spotify auth token, is created with overly broad permissions

## Summary
Severity: High
Advisory: GHSA-pwhh-q4h6-w599
CVE: CVE-2025-27154
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-28
Source: https://github.com/advisories/GHSA-pwhh-q4h6-w599
Type: github-advisory

## Affected
- PyPI: `spotipy` — affected >=0 <2.25.1

## Details
### Summary

The `CacheHandler` class creates a cache file to store the auth token here: https://github.com/spotipy-dev/spotipy/blob/master/spotipy/cache_handler.py#L93-L98

The file created has `rw-r--r--` (644) permissions by default, when it could be locked down to `rw-------` (600) permissions. I think `600` is a sensible default.

![image](https://github.com/user-attachments/assets/0b7ebbc1-a27a-4528-ab6a-135c7886766a)

### Details

This leads to overly broad exposure of the spotify auth token. If this token can be read by an attacker (another user on the machine, or a process running as another user), it can be used to perform administrative actions on the Spotify account, depending on the scope granted to the token.

### PoC

Run an application that uses spotipy with client creation like this:

```python
from pathlib import Path
import spotipy
from os import getenv

def create_spotify_client(client_id: str, client_secret: str) -> spotipy.Spotify:
    """Create and return an authenticated Spotify client.

    Args:
        client_id: Spotify API client ID
        client_secret: Spotify API client secret

    Returns:
        An authenticated Spotify client instance
    """
    cache_path = Path.home() / ".cache" / "spotify-backup/.auth_cache"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=str(cache_path))

    client = spotipy.Spotify(
        auth_manager=spotipy.oauth2.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8000/callback",
            cache_handler=cache_handler,
            scope=[
                "user-library-read",
                "playlist-read-private",
                "playlist-read-collaborative",
            ],
        )
    )

    return client

create_spotify_client()
```

And then check the file permissions on the cache file that was created with:

```bash
$ ls -la ~/.cache/spotify-backup/.auth_cache`
.rw-r--r--. alichtman alichtman 562 B Thu Feb 20 02:12:33 2025  /home/alichtman/.cache/spotify-backup/.auth_cache
```

If this issue is combined with another misconfiguration, like having `o+r` permissions set on your home directory, an attacker will be able to read this file and steal this auth token.

Good defense in depth would be to restrict read permissions on this cache file that contains an auth token

### Impact

Potential exposure of Spotify auth token to other users with access to the machine. A worst case scenario is if the token is granted all permissions, and can be used to do any of:

- exfiltrate spotify likes / saved playlists
- delete your content
- modify your content w/o your permission

If someone were to discover an RCE in Spotify that you could trigger on a machine by having a song played (or song metadata parsed or something), this auth token could maybe be used to add a song to a playlist, or control playback (allowing further exploitation).

## References
- https://github.com/spotipy-dev/spotipy/security/advisories/GHSA-pwhh-q4h6-w599
- https://nvd.nist.gov/vuln/detail/CVE-2025-27154
- https://github.com/spotipy-dev/spotipy/commit/1ca453f6ef87a2a9e9876f52b6cb38d13532ccf2
- https://github.com/spotipy-dev/spotipy
- https://github.com/spotipy-dev/spotipy/blob/master/spotipy/cache_handler.py#L93-L98
- https://github.com/spotipy-dev/spotipy/releases/tag/2.25.1
