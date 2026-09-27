# [H] Frigate unsafe deserialization in `load_config_with_no_duplicates` of `frigate/util/builtin.py`

## Summary
Severity: High
Advisory: CVE-2023-45672
Aliases: GHSA-qp3h-4q62-p428
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-10-30
Source: https://osv.dev/vulnerability/CVE-2023-45672
Type: osv

## Details
Frigate is an open source network video recorder. Prior to version 0.13.0 Beta 3, an unsafe deserialization vulnerability was identified in the endpoints used to save configurations for Frigate. This can lead to unauthenticated remote code execution. This can be performed through the UI at `/config` or through a direct call to `/api/config/save`. Exploiting this vulnerability requires the attacker to both know very specific information about a user's Frigate server and requires an authenticated user to be tricked into clicking a specially crafted link to their Frigate instance. This vulnerability could exploited by an attacker under the following circumstances: Frigate publicly exposed to the internet (even with authentication); attacker knows the address of a user's Frigate instance; attacker crafts a specialized page which links to the user's Frigate instance; attacker finds a way to get an authenticated user to visit their specialized page and click the button/link. Input is initially accepted through `http.py`. The user-provided input is then parsed and loaded by `load_config_with_no_duplicates`. However, `load_config_with_no_duplicates` does not sanitize this input by merit of using `yaml.loader.Loader` which can instantiate custom constructors. A provided payload will be executed directly at `frigate/util/builtin.py:110`. This issue may lead to pre-authenticated Remote Code Execution. Version 0.13.0 Beta 3 contains a patch.

## References
- https://github.com/blakeblackshear/frigate/blob/5658e5a4cc7376504af9de5e1eff178939a13e7f/frigate/config.py#L1244-L1244
- https://github.com/blakeblackshear/frigate/blob/5658e5a4cc7376504af9de5e1eff178939a13e7f/frigate/http.py#L998-L998
- https://github.com/blakeblackshear/frigate/blob/5658e5a4cc7376504af9de5e1eff178939a13e7f/frigate/util/builtin.py#L110-L110
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45672.json
- https://github.com/blakeblackshear/frigate/security/advisories/GHSA-qp3h-4q62-p428
- https://nvd.nist.gov/vuln/detail/CVE-2023-45672
- https://securitylab.github.com/advisories/GHSL-2023-190_Frigate/
