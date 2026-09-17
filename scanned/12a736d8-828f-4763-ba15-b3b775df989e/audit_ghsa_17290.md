# [H] 1Panel – CAPTCHA Bypass via Client-Controlled Flag 

## Summary
Severity: High
Advisory: GHSA-qmg5-v42x-qqhq
CVE: CVE-2025-66507
CWE: CWE-290, CWE-602, CWE-807
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-qmg5-v42x-qqhq
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=0 <2.0.14
- Go: `github.com/1Panel-dev/1Panel/core` — affected >=0 <0.0.0-20251128030527-ac43f00273be

## Details
### Summary

A CAPTCHA bypass vulnerability in the 1Panel authentication API allows an unauthenticated attacker to disable CAPTCHA verification by abusing a client-controlled parameter. Because the server previously trusted this value without proper validation, CAPTCHA protections could be bypassed, enabling automated login attempts and significantly increasing the risk of account takeover (ATO).

### Details

The /api/login endpoint accepts a boolean field named ignoreCaptcha directly from the client request body:

`"ignoreCaptcha": true`


The backend implementation uses this value to determine whether CAPTCHA validation should be performed:

```
if !req.IgnoreCaptcha {
    if errMsg := captcha.VerifyCode(req.CaptchaID, req.Captcha); errMsg != "" {
        helper.BadAuth(c, errMsg, nil)
        return
    }
}

```

Because req.IgnoreCaptcha is taken directly from user input—with no server-side validation, no session binding, and no privilege checks—any unauthenticated attacker can force CAPTCHA validation to be skipped.

There are no additional conditions, such as:

no requirement for MFA

no trusted device

no IP reputation checks

no prior valid session

no rate limiting

This results in CAPTCHA being entirely client-controlled, which violates fundamental authentication and anti-automation security assumptions.

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-qmg5-v42x-qqhq
- https://nvd.nist.gov/vuln/detail/CVE-2025-66507
- https://github.com/1Panel-dev/1Panel/commit/ac43f00273be745f8d04b90b6e2b9c1a40ef7bca
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases/tag/v2.0.14
