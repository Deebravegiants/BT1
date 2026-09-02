### Title
Webhook `shop` (tenant) identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC computed only over the raw request body, but the `shop` (tenant identity) used by the rest of the pipeline is read from an unsigned HTTP header. This is the same bug class as the reported "wrong account bound" issue: the code validates one thing (`raw_body`) but acts on a different, uncovered field (`shop-domain` header) to determine which tenant/shop the webhook belongs to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived independently, from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only proves that `raw_body` was signed with `Context.api_secret_key`; it says nothing about which shop the header claims to be from: [3](#0-2) 

The identity binding that should hold is: `shop authenticated by HMAC == shop used by the app to process/route the webhook`. Because `shop` comes from a header outside the signed payload, that equality is not enforced — the byte range verified (`@raw_body`) is not the byte range parsed for tenant identity (`headers["shopify-shop-domain"]`). Any party able to obtain one validly-signed webhook body for their own shop (trivial — a merchant/attacker just triggers an event on their own store that the app is subscribed to) can capture that body/HMAC pair and replay it with an arbitrary `x-shopify-shop-domain` header value, since the header is not part of what's signed.

### Impact Explanation
The `shop` field returned by `Request#shop` is what host applications use to key their handler dispatch and per-tenant data (see `RegistryTest`, where the handler receives `data.shop` and acts on it) — i.e., it decides which merchant's session/data the incoming event is attributed to. Because this value is not bound to the HMAC, an attacker can forge the tenant identity of an otherwise validly-signed webhook payload and cause the app to process/store data under a different shop's identity than the one that produced the payload — a cross-tenant identity confusion. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate: the attacker needs (a) their own shop installed on the target app (to obtain a validly HMAC-signed webhook body/hmac pair) and (b) the ability to replay/forward that request with a modified `shop-domain` header to the app's webhook endpoint. Both are attainable by any unprivileged merchant using the app, without needing `api_secret_key` or any privileged credential — it only requires ordinary use of the app as a legitimate but adversarial tenant.

### Recommendation
Include the shop domain (and other identity-relevant headers such as `topic`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signed body before trusting it for tenant routing. At minimum, document that consuming applications must independently verify that `data.shop` corresponds to a shop actually installed/known to the app before acting on the webhook.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` (attacker's own store) and on `victim-shop.myshopify.com`.
2. Attacker triggers a webhook-eligible event on their own store; Shopify sends a POST with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts/replays this exact request to the app's webhook endpoint but rewrites the header to `x-shopify-shop-domain: victim-shop.myshopify.com`, leaving body `B` and the hmac header untouched.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (body/hmac unchanged), and `ShopifyAPI::Webhooks::Registry.process` dispatches the handler with `data.shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store — confirmed by: [4](#0-3)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
