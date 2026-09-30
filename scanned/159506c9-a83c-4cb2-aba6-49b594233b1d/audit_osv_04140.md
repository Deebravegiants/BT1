# [C] Apache APISIX: the body_schema check in request-validation plugin can be bypassed

## Summary
Severity: Critical
Advisory: BIT-apisix-2022-25757
Aliases: CVE-2022-25757
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-apisix-2022-25757
Type: osv

## Affected
- Bitnami: `apisix` — affected >=0 <2.13.0

## Details
In Apache APISIX before 2.13.0, when decoding JSON with duplicate keys, lua-cjson will choose the last occurred value as the result. By passing a JSON with a duplicate key, the attacker can bypass the body_schema validation in the request-validation plugin. For example, `{"string_payload":"bad","string_payload":"good"}` can be used to hide the "bad" input. Systems satisfy three conditions below are affected by this attack: 1. use body_schema validation in the request-validation plugin 2. upstream application uses a special JSON library that chooses the first occurred value, like jsoniter or gojay 3. upstream application does not validate the input anymore. The fix in APISIX is to re-encode the validated JSON input back into the request body at the side of APISIX. Improper Input Validation vulnerability in __COMPONENT__ of Apache APISIX allows an attacker to __IMPACT__. This issue affects Apache APISIX Apache APISIX version 2.12.1 and prior versions.

## References
- http://www.openwall.com/lists/oss-security/2022/03/28/2
- https://lists.apache.org/thread/03vd2j81krxmpz6xo8p1dl642flpo6fv
- https://nvd.nist.gov/vuln/detail/CVE-2022-25757
