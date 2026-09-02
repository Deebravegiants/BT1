### Title
Webhook shop-domain spoofing: `shop` header is trusted but not covered by HMAC verification - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the payload bytes but never binds the `X-Shopify-Shop-Domain` header to that signature. The library still trusts `request.shop` (taken straight from the unauthenticated header) when dispatching the webhook to the registered handler, breaking the identity binding `hmac_signed_bytes == bytes_used_to_derive_tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts the `shop` used for tenant identification purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header: [1](#0-0) 

Its `to_signable_string`, which is what the HMAC is computed and verified over, only returns the raw body: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the `hmac` header using a secure compare, but the `shop` header value plays no role at all in that computation: [3](#0-2) 

`Webhooks::Registry.process` only checks that the HMAC over the body is valid, then immediately trusts `request.shop` for dispatch to the app's handler: [4](#0-3) 

Because Shopify signs webhook payloads with the app's single, app-wide `client_secret` (the same secret is used for every shop that installs the app — this mirrors `Context.api_secret_key` used here), a valid HMAC only proves "this body came from Shopify for this app," not "this body belongs to this specific shop." The `shop-domain` header is never part of the signed material, so it can be swapped for any value without invalidating the signature.

### Impact Explanation
Any internet user can install the target app on their own (attacker-controlled) development/test store — this is an unprivileged, self-service action requiring no special access. When Shopify sends a legitimate webhook for an event on that attacker-owned store, the attacker captures the exact HTTP request (valid HMAC, since it is computed only over the body using the shared app secret). The attacker then replays that same request to the app's webhook endpoint, substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (body unchanged), and `Registry.process` calls the app's handler with `shop: "victim-store.myshopify.com"` while the payload content is entirely attacker-controlled. If the host application's webhook handler (as is standard practice, and as demonstrated by the library's own `WebhookMetadata` design) uses the `shop` field to look up the merchant session, authorize actions, or persist/update data keyed by shop, the attacker achieves cross-tenant data injection/corruption under a victim's identity without ever compromising the victim's credentials.

### Likelihood Explanation
High. No secrets or privileged access are required beyond the ability to install/interact with the app as a normal merchant (which any internet user can do for a public or dev-store app), and simple HTTP replay with a modified header is trivial to perform.

### Recommendation
Include the shop-domain (and topic/webhook-id) header value in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the payload before trusting `request.shop` for dispatch — e.g., verify the shop domain against session/install records maintained by the app rather than relying solely on the header, or require it to be part of `to_signable_string`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a genuine webhook POST, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {...attacker-controlled order payload...}
   ```
2. Attacker resends the identical request to the app's webhook endpoint, changing only the shop header:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the HMAC (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The registered handler is invoked with `shop: "victim-shop.myshopify.com"` and attacker-controlled body data (`lib/shopify_api/webhooks/registry.rb:188-199`), letting the attacker impersonate the victim tenant in any shop-keyed logic in the host application.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
