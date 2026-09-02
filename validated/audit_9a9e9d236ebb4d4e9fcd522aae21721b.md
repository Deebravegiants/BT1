Based on my analysis, I've confirmed the root cause with exact file/method support. Here is the finding.

### Title
Webhook shop-domain identity is not bound to the HMAC signature, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC, then trusts the `shop` value taken from an unauthenticated header to identify which merchant the event belongs to. Because the HMAC signable string only covers the raw body, any attacker who can obtain one valid `(raw_body, hmac)` pair for their own shop can replay it with a forged `shop-domain` header for a victim shop and pass validation.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` and defines the signable string as only the raw body: [1](#0-0) 

The `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers, which are not part of the signed content at all: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the raw body) and compares it to the `hmac` header — it never binds `shop` or any other header to the signature: [3](#0-2) 

`Registry.process` uses this same unauthenticated `request.shop` value as the tenant identity handed to the app's webhook handler once HMAC validation succeeds: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified bytes == bytes used to identify the tenant`. In reality, `HMAC-verified bytes == raw_body only`, while `tenant identity == request.shop header`, an entirely separate, unauthenticated channel. An attacker who legitimately owns a Shopify store, receives real webhooks for it (with genuine `hmac-sha256` and body pairs computed with the app's real secret), can replay that exact `(raw_body, hmac)` pair while substituting the `shopify-shop-domain` header for any victim `myshopify.com` domain. `HmacValidator.validate` still succeeds because it never looks at the header, and the handler receives `WebhookMetadata` claiming to originate from the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem hands host applications a `shop` value that has passed HMAC "validation" logically but is not actually authenticated. Any app that relies on `WebhookMetadata#shop` (as recommended/expected usage of this gem, see `Registry.process`) to select which merchant record to read/write can be tricked into performing actions attributed to, or against, a shop the attacker does not control — meeting the "cross-tenant access" bar, achievable by any unprivileged Shopify merchant/attacker with no access token or credential belonging to the victim.

### Likelihood Explanation
Likelihood is high for any embedding app that follows the documented webhook flow (`Registry.add_registration` + `Registry.process`) and trusts the `shop` field from `WebhookMetadata`, which is the library's own recommended attribute for tenant identification. The attacker only needs to be a legitimate merchant of the app (trivial to obtain by installing a free/dev Shopify store) to capture one valid `(body, hmac)` pair, then replay it against the app's public webhook endpoint with an altered `shop-domain` header.

### Recommendation
- Short term: Include the `shop-domain` (and `topic`/`webhook-id`) header values in the signable string used by `HmacValidator`, or otherwise cryptographically bind them to the verified payload, so that `to_signable_string` output equals everything the caller subsequently trusts.
- Long term: Redesign `VerifiableQuery`/`Request` so a caller cannot obtain a "validated" object whose trusted fields (`shop`, `topic`, `webhook_id`) are disjoint from the bytes actually covered by the HMAC — e.g., have `HmacValidator.validate` return/attach only the fields it verified, rather than allowing separate unauthenticated accessors on the same object.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify sends a real webhook to the app's endpoint with a legitimate body `B` and header `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(secret, B)`, plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `B` and `H`, then sends their own HTTP request to the same webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only [1](#0-0)  and it matches `H`, so validation passes.
5. `Registry.process` invokes the app handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed body of B, ...)` [5](#0-4) , causing the app to process attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
