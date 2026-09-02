### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, while the `shop` identity used to route the payload to the app's tenant-specific handler is read from an HTTP header that is completely outside that signed content. This breaks the identity binding: `shop authenticated by HMAC == shop the data is attributed to`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor is derived from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never part of the signed content: [2](#0-1) 

`Registry.process` verifies only the HMAC over that signable string (the body) and then dispatches to the app's handler using `request.shop` taken directly from the unauthenticated header: [3](#0-2) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received signature — for webhook requests this is exclusively the body bytes, never the shop domain: [4](#0-3) 

Because Shopify's real webhook HMAC (documented and mirrored by this gem) is computed only over the request body, any entity that operates its own shop with the app installed will receive genuinely-signed webhooks (valid `X-Shopify-Hmac-Sha256` for a given body) addressed to their own store. Since the `X-Shopify-Shop-Domain` header is not part of what's signed, that attacker can replay the exact same body + HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes (the body and signature are unchanged and valid), and `Registry.process` forwards `WebhookMetadata` with `shop: <victim>` and the attacker-controlled body to the handler, which the host application will use to update state believed to belong to the victim tenant.

### Impact Explanation
This is a cross-tenant identity-binding failure: the gem authenticates *bytes*, not the *tenant* those bytes are attributed to. A multi-tenant app relying on this library's webhook validation to determine which shop a payload belongs to can be made to process attacker-supplied, validly-signed webhook bodies under a victim shop's identity — e.g. injecting fake `orders/create`, `app/uninstalled`, GDPR, or billing-related webhook data attributed to another merchant. This matches the "Critical – cross-tenant access" impact bucket, since it lets one tenant inject data that the host application will trust as originating from another tenant.

### Likelihood Explanation
Likelihood is realistic though bounded: it requires the attacker to control (or install the target app on) at least one legitimate shop so Shopify will generate genuinely HMAC-signed webhook traffic for them — this is achievable by any unprivileged internet user for public apps (no `api_secret_key`, access token, or other privileged credential is needed; Shopify itself computes the valid signature for the attacker's own store's events). The attacker only needs to capture one such body+HMAC pair and resend it with a modified shop-domain header. This does not require TLS interception, local access, or social engineering.

### Recommendation
Bind the tenant identity into the authenticated material before trusting it: either (a) include the `shop-domain` (and ideally `topic`/`webhook-id`) header value in the string that is HMAC-verified (`to_signable_string`), or (b) require the caller to look up the shop's own per-shop secret/session by an already-authenticated identifier rather than trusting the header as-is, and reject requests where the header-derived shop cannot be independently corroborated (e.g. cross-check against a known installed-shop list keyed off something already bound to the signature, or validate the header hasn't been tampered with via a separate signed channel).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a normal, unprivileged action for a public app).
2. Attacker triggers/observes a real webhook Shopify sends to the app's endpoint for their own shop, e.g.:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-signature-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: ...
   Body: {"id": 123, "note": "malicious content"}
   ```
   This is a legitimately signed body+HMAC pair since Shopify itself created it for the attacker's store.
3. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` value to the same endpoint, only changing:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new` parses the modified headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the signature only over `@raw_body` (unchanged) — validation succeeds. [3](#0-2) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` and the host application processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`, breaking the equality `shop authenticated by HMAC == shop the data is attributed to`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
