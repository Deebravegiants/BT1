# [H] Apprise vulnerable to regex injection with IFTTT Plugin

## Summary
Severity: High
Advisory: GHSA-qhmp-h54x-38qr
CVE: CVE-2021-39229
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-qhmp-h54x-38qr
Type: github-advisory

## Affected
- PyPI: `apprise` — affected >=0 <0.9.5.1

## Details
### Impact
Anyone _publicly_ hosting the Apprise library and granting them access to the IFTTT notification service.

### Patches
Update to Apprise v0.9.5.1
   ```bash
   # Install Apprise v0.9.5.1 from PyPI
   pip install apprise==0.9.5.1
   ```

The patch to the problem was performed [here](https://github.com/caronc/apprise/pull/436/files).

### Workarounds
Alternatively, if upgrading is not an option, you can safely remove the following file:
- `apprise/plugins/NotifyIFTTT.py` 

The above will eliminate the ability to use IFTTT, but everything else will work smoothly.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Apprise](https://github.com/caronc/apprise/issues)
* Email me at [lead2gold@gmail.com](mailto:lead2gold@gmail.com)

### Additional Credit
Github would not allow me to additionally credit **Rasmus Petersen**, but I would like to put that here at the very least - thank you for finding and reporting this issue along with those already credited

## Additional Notes:
- Github would not allow me to add/tag the 2 CWE's this issue is applicable to (only CWE-400).  The other is: CWE-730 (placed in the title)

## References
- https://github.com/caronc/apprise/security/advisories/GHSA-qhmp-h54x-38qr
- https://nvd.nist.gov/vuln/detail/CVE-2021-39229
- https://github.com/caronc/apprise/pull/436
- https://github.com/caronc/apprise/commit/e20fce630d55e4ca9b0a1e325a5fea6997489831
- https://github.com/caronc/apprise
- https://github.com/caronc/apprise/blob/0007eade20934ddef0aba38b8f1aad980cfff253/apprise/plugins/NotifyIFTTT.py#L356-L359
- https://github.com/caronc/apprise/releases/tag/v0.9.5.1
- https://github.com/pypa/advisory-database/tree/main/vulns/apprise/PYSEC-2021-327.yaml
