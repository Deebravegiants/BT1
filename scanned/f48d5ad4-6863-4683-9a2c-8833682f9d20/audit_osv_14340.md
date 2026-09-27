# [C] CVE-2018-9230

## Summary
Severity: Critical
Advisory: CVE-2018-9230
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-02
Source: https://osv.dev/vulnerability/CVE-2018-9230
Type: osv

## Details
In OpenResty through 1.13.6.1, URI parameters are obtained using the ngx.req.get_uri_args and ngx.req.get_post_args functions that ignore parameters beyond the hundredth one, which might allow remote attackers to bypass intended access restrictions or interfere with certain Web Application Firewall (ngx_lua_waf or X-WAF) products. NOTE: the vendor has reported that 100 parameters is an intentional default setting, but is adjustable within the API. The vendor's position is that a security-relevant misuse of the API by a WAF product is a vulnerability in the WAF product, not a vulnerability in OpenResty

## References
- https://openresty.org/en/changelog-1013006.html
- https://github.com/Bypass007/vuln/blob/master/OpenResty/Uri%20parameter%20overflow%20in%20Openresty.md
