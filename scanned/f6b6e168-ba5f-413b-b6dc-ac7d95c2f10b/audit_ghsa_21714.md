# [H] Server crash if running Python 3.10 w/ Sanic 20.12

## Summary
Severity: High
Advisory: GHSA-7p79-6x2v-5h88
Ecosystem: PyPI
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-7p79-6x2v-5h88
Type: github-advisory

## Affected
- PyPI: `sanic` — affected >=0.1.7 <20.12.6

## Details
**!!! ONLY APPLIES TO VERSIONS PRIOR TO Sanic v20.12 WHEN USING Python 3.10 !!!**

Sanic v20.12 officially supports Python versions 3.6, 3.7, 3.8, and 3.9. However, if you accidentally run it with version 3.10 (**which is not supported by Sanic 20.12**), your server is prone to crashing on an incoming web request.

### Impact
Anyone running Sanic server between 0.1.7 and 20.12 **using Python 3.10**.

### Patches
[Sanic v20.12.6](https://github.com/sanic-org/sanic/releases/tag/v20.12.6)

### Workarounds
Use a supported version of Python (v3.6 - v3.9)

### References
> In [asyncio](https://docs.python.org/3/library/asyncio.html#module-asyncio), the explicit passing of a loop argument has been deprecated and will be removed in version 3.10 for the following: ... [asyncio.Event](https://docs.python.org/3/library/asyncio-sync.html#asyncio.Event)

[Python 3.8 Release Notes](https://docs.python.org/3/whatsnew/3.8.html#deprecated)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the community forums](https://community.sanicframework.org/)
* Ping us on [the Discord server](https://discord.gg/FARQzAEMAA)

## References
- https://github.com/sanic-org/sanic/security/advisories/GHSA-7p79-6x2v-5h88
- https://github.com/sanic-org/sanic
- https://github.com/sanic-org/sanic/releases/tag/v20.12.6
