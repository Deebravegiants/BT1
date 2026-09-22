# [C] PYSEC-2024-20

## Summary
Severity: Critical
Advisory: PYSEC-2024-20
Aliases: CVE-2024-22203, GHSA-q97g-c29h-x2p7
Ecosystem: PyPI
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/PYSEC-2024-20
Type: osv

## Affected
- PyPI: `whoogle-search` — affected >=0 <3a2e0b262e4a076a20416b45e6b6f23fd265aeda, >=0 <0.8.4

## Details
Whoogle Search is a self-hosted metasearch engine. In versions prior to 0.8.4, the `element` method in `app/routes.py` does not validate the user-controlled `src_type` and `element_url` variables and passes them to the `send` method which sends a GET request on lines 339-343 in `request.py`, which leads to a server-side request forgery. This issue allows for crafting GET requests to internal and external resources on behalf of the server. For example, this issue would allow for accessing resources on the internal network that the server has access to, even though these resources may not be accessible on the internet. This issue is fixed in version 0.8.4.

## References
- https://securitylab.github.com/advisories/GHSL-2023-186_GHSL-2023-189_benbusby_whoogle-search/
- https://securitylab.github.com/advisories/GHSL-2023-186_GHSL-2023-189_benbusby_whoogle-search/
- https://github.com/benbusby/whoogle-search/commit/3a2e0b262e4a076a20416b45e6b6f23fd265aeda
- https://github.com/benbusby/whoogle-search/blob/92e8ede24e9277a5440d403f75877209f1269884/app/request.py#L339-L343
- https://github.com/benbusby/whoogle-search/blob/92e8ede24e9277a5440d403f75877209f1269884/app/routes.py#L465-L490
- https://github.com/benbusby/whoogle-search/blob/92e8ede24e9277a5440d403f75877209f1269884/app/routes.py#L466
- https://github.com/benbusby/whoogle-search/blob/92e8ede24e9277a5440d403f75877209f1269884/app/routes.py#L476
- https://github.com/benbusby/whoogle-search/blob/92e8ede24e9277a5440d403f75877209f1269884/app/routes.py#L479
- https://github.com/advisories/GHSA-q97g-c29h-x2p7
