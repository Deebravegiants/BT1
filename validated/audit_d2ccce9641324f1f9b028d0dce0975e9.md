### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant event spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, while the `shop` attribute that the handler uses to attribute the event to a tenant is taken from an unsigned HTTP header. This breaks the identity binding: `shop authenticated == shop acted on`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` reads the shop identity from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, a value that is completely outside the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the body) using the app's shared `client_secret`: [3](#0-2) 

`Registry.process` gates only on this body HMAC check, then constructs the event metadata using the unauthenticated `shop` header and dispatches it to the handler: [4](#0-3) 

Because the same `client_secret` HMAC key is shared by every shop that installs a given app, any unprivileged user who can install the app on their own shop (a free/dev store) receives genuine webhooks with a valid HMAC over an attacker-controlled body. That captured `(raw_body, hmac)` pair remains valid for **any** value of the `shop-domain` header, since the header is never part of the signed content. The attacker can POST the same body and HMAC to the app's public webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `HmacValidator.validate` will accept it, and the handler will receive `WebhookMetadata` claiming the event belongs to the victim shop, even though the body content was fully attacker-chosen from their own store's events.

This is exactly the "field acted on but not covered by the HMAC" identity-binding failure: the equality the library implicitly promises to handler code — `verified(hmac) == (shop, topic, body)` — actually only holds for `body`, not `shop`.

### Impact Explanation
This enables cross-tenant data confusion/injection: an attacker-controlled webhook payload can be attributed to any target shop known to the app. Depending on how the host application uses `WebhookMetadata#shop` (e.g., looking up the shop's session/store record and writing the body's contents against it, such as product/order/customer data, or GDPR redact topics), this can lead to writing or processing attacker-supplied data under a victim tenant's identity — a cross-tenant access/integrity violation, which maps to the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is realistic but requires two unprivileged capabilities that are within reach of any internet user: (1) install the target app on their own low-cost/free development store, generating real, validly-signed webhook payloads for events they control, and (2) send an HTTP POST directly to the app's public webhook endpoint with a forged `shop-domain` header. Both are attacker-controlled with no privileged credentials, tokens, or `client_secret` needed. The only defense is if the host application performs an out-of-band comparison between the header shop and a known-good session lookup — but the gem itself does not enforce this binding.

### Recommendation
- Bind the `shop` (and ideally `topic`/`webhook-id`) values into the authenticated content before HMAC verification, or otherwise cryptographically tie them to the signed body (e.g., include them in the value passed to `HmacValidator.validate`/`to_signable_string`).
- At minimum, document and enforce in `Registry.process` that the caller must independently verify `request.shop` against a known, previously-established session/shop record before trusting it, and consider raising if `shop` cannot be corroborated against an existing installed session.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop, `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event on their shop with a body they can influence (e.g., updates a product's title to attacker-chosen data), receiving from Shopify a genuine request:
   - `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body, keyed with app client_secret>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `raw_body: <attacker-controlled JSON>`
3. Attacker replays this exact `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but changes the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `raw_body` — this passes. [4](#0-3) 
5. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-crafted body, believing the data legitimately originates from the victim's shop.

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
