# [H] Voilà Local file inclusion

## Summary
Severity: High
Advisory: GHSA-2q59-h24c-w6fg
CVE: CVE-2024-30265
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-04-03
Source: https://github.com/advisories/GHSA-2q59-h24c-w6fg
Type: github-advisory

## Affected
- PyPI: `voila` — affected >=0.0.2 <0.2.17
- PyPI: `voila` — affected >=0.3.0a0 <0.3.8
- PyPI: `voila` — affected >=0.4.0a0 <0.4.4
- PyPI: `voila` — affected >=0.5.0a0 <0.5.6

## Details
### Impact

Any deployment of voilà dashboard allow local file inclusion, that is to say any file on a filesystem that is readable by the user that runs the voilà dashboard server can be downloaded by someone with network access to the server. 

Whether this still requires authentication depends on how voilà is deployed.

### Patches

This is patched in 0.2.17+, 0.3.8+, 0.4.4+, 0.5.6+

### Workarounds

None.


### References

CWE-73: External Control of File Name or Path


### Original report

I have found a local file inclusion vulnerability in one of your subprojects, voila (https://github.com/voila-dashboards/voila).

The vulnerability exists in the "/static" Route, and can be exploited by simply making a request such as this:

```
$ curl localhost:8866/static/etc/passwd
```

...or by using a webbrowser to download the file.

I dug into the source code, and I think the offending line is here: https://github.com/voila-dashboards/voila/blob/8419cc7d79c0bb1dabfbd9ec49cb957740609d4d/voila/app.py#L664
`"static_path"` gets set to `"/"`, irrespective of the actual `"--static"` cli option. Because of that, the `tornado.web.StaticFileHandler` gets initialized with `path="/"`. Then, `tornado.web.StaticFileHandler.get` calls `tornado.web.StaticFileHandler.get_absolute_path` with `root="/"` and `path="[USER SUPPLIED PATH]"`, which leads to local file inclusion. An attacker can request any file on the system they want (that the user running voila has access to).

I suspect this was an oversight during development. Setting `static_path=self.static_root` (the aforementioned correct cli option) in line 664 provides the intended behavior and restricts the file access to the static directory.
From what I can tell, this line has been in the repository since September 2018. This is the commit that added it: https://github.com/voila-dashboards/voila/commit/28faacc9b03b160fd8fa920ad045f4ec0667ab67

I have found multiple voila instances online that are impacted, such as:
- ... [redacted]
- ... [redacted]
- ... [redacted]

...but many more probably exist. They're easy to identify by `[redacted]` Therefore the Issue should be fixed as soon as possible, and a security advisory should be released to inform the impacted users.

## References
- https://github.com/voila-dashboards/voila/security/advisories/GHSA-2q59-h24c-w6fg
- https://nvd.nist.gov/vuln/detail/CVE-2024-30265
- https://github.com/voila-dashboards/voila/commit/00d6362c237b6b4d466873535554d6076ead0c52
- https://github.com/voila-dashboards/voila/commit/28faacc9b03b160fd8fa920ad045f4ec0667ab67
- https://github.com/voila-dashboards/voila/commit/5542e4ae36bb5d184deaa48f95e76be477756af2
- https://github.com/voila-dashboards/voila/commit/98b6a40fec27723572314fdbba99bdc147d904c8
- https://github.com/voila-dashboards/voila/commit/c045be6988539d07cceeb9f82fc660a49485d504
- https://github.com/voila-dashboards/voila
