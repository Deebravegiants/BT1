# [C] Absolute Path Traversal due to incorrect use of `send_file` call in Piano LED Visualizer

## Summary
Severity: Critical
Advisory: CVE-2022-24900
Aliases: GHSA-g78x-q3x8-r6m4
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L)
Published: 2022-04-29
Source: https://osv.dev/vulnerability/CVE-2022-24900
Type: osv

## Details
Piano LED Visualizer is software that allows LED lights to light up as a person plays a piano connected to a computer. Version 1.3 and prior are vulnerable to a path traversal attack. The `os.path.join` call is unsafe for use with untrusted input. When the `os.path.join` call encounters an absolute path, it ignores all the parameters it has encountered till that point and starts working with the new absolute path. Since the "malicious" parameter represents an absolute path, the result of `os.path.join` ignores the static directory completely. Hence, untrusted input is passed via the `os.path.join` call to `flask.send_file` can lead to path traversal attacks. A patch with a fix is available on the `master` branch of the GitHub repository. This can also be fixed by preventing flow of untrusted data to the vulnerable `send_file` function. In case the application logic necessiates this behaviour, one can either use the `flask.safe_join` to join untrusted paths or replace `flask.send_file` calls with `flask.send_from_directory` calls.

## References
- https://github.com/onlaj/Piano-LED-Visualizer/blob/6a732caa812c83a807c711f3d091af99209cae7b/webinterface/views_api.py#L970
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24900.json
- https://github.com/onlaj/Piano-LED-Visualizer/security/advisories/GHSA-g78x-q3x8-r6m4
- https://nvd.nist.gov/vuln/detail/CVE-2022-24900
- https://github.com/onlaj/Piano-LED-Visualizer/issues/350
- https://github.com/onlaj/Piano-LED-Visualizer/commit/3f10602323cd8184e1c69a76b815655597bf0ee5
- https://github.com/onlaj/Piano-LED-Visualizer/pull/351
