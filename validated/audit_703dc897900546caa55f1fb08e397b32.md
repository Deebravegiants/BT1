## Title
Webhook shop-tenant spoofing via HMAC that only covers the request body, not the `shop-domain` identity header - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw JSON body, then dispatches to the app's handler using a `shop` value that is taken from a separate, unauthenticated header. Because the shared `api_secret_key` used to compute the HMAC is common to every shop that has installed the app (it is not per-tenant), any shop owner (including an attacker who installs the app on their own free/dev store) can obtain a body+HMAC pair that Shopify signs for them, then replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. The signature check still passes, and the handler receives attacker-controlled `body` content attributed to the victim `shop`.

## Finding Description
- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `#hmac` reads the `hmac-sha256` header: [1](#0-0) 
- `shop` is read from a completely separate header (`shop-domain`) that plays no part in the signed content: [2](#0-1) 
- `Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) using `Context.api_secret_key`: [3](#0-2) 
- `Registry.process` accepts the request once that body-only HMAC validates, then forwards `request.shop` — the unauthenticated header — straight into `WebhookMetadata`, which is the tenant-identifying field the handler acts on: [4](#0-3) 

The identity binding that should hold is: `shop header == shop the HMAC secret was minted for`. Instead, the code enforces only `HMAC(raw_body) == valid`, while `shop` is copied out of an unauthenticated header. Since `api_secret_key` is the same for every shop that installs the app, an attacker who is a legitimate (even free/dev) installer of the target app can:
1. Trigger any webhook topic in their own shop to receive a genuinely-signed `(raw_body, hmac)` pair from Shopify.
2. Replay that exact body and HMAC to the app's webhook endpoint, but swap the `X-Shopify-Shop-Domain` header to the victim's `myshopify.com` domain.
3. `HmacValidator.validate` still succeeds (it never looked at the shop header), and the app's handler processes attacker-chosen body content as if it originated from the victim shop.

## Impact Explanation
This breaks the tenant boundary the webhook mechanism is supposed to enforce: `shop == owner of the HMAC that validated`. Any handler that uses `WebhookMetadata#shop` to look up/update per-merchant records (the documented and expected usage pattern) can be made to apply attacker-supplied webhook payloads to a different merchant's tenant record, i.e., cross-tenant data injection/corruption using only the ability to install the app on one's own store — no leaked credentials or privileged access required.

## Likelihood Explanation
Any internet user can install a public Shopify app on a free development store to obtain legitimately signed webhook bodies, since `api_secret_key` is shared across all installs of the app rather than per-shop. Forging the `shop-domain` header on the replayed HTTP request requires no cryptographic material — it is a plain, unauthenticated header.

## Recommendation
Bind the `shop` identity into the value that is HMAC-verified — e.g., verify the webhook using a per-shop secret/token, or include the `shop-domain` (and other identity-relevant headers) in the signable string that `HmacValidator` checks, so a valid signature can only be produced for the header/body combination Shopify actually sent.

## Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) to capture a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the app's shared `api_secret_key`.
2. Send a POST to the app's webhook endpoint with the captured `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — it succeeds.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the host application to act on attacker data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
